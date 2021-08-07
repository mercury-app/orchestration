import json
import logging

from tornado.websocket import WebSocketClosedError

from mercury.node import MercuryNode

from server.views import MercuryHandler, MercuryWsHandler
from server.views.utils import (
    get_node_attrs,
    get_node_input_code_snippet,
    get_node_output_code_snippet,
)

logger = logging.getLogger(__name__)

JUPYTER_PORT = "8888"


class NodeHandler(MercuryHandler):
    # decorator to wrap and create a json api response, wrap in data, attributes, types
    json_type = "nodes"

    def get(self, node_id=None):
        """Returns the node(s) available
        ---
        tags: [Nodes]
        summary: Get nodes.
        parameters:
          - in: path
            name: node_id
            type: string
            required: false
            description: (OPTIONAL) unique node id for a specific node.
        description: Get the nodes in the DAG
        responses:
            200:
                description: List of node(s) and their container
                content:
                    application/json:
                        schema:
                            type: array
                            items:
                                NoSchema
        """
        if node_id:
            node = self.application.dag.get_node(node_id)
            nodes = [node]
        else:
            nodes = self.application.dag.nodes

        data = []

        for node in nodes:
            node_response = {
                "id": node.id,
                "type": self.json_type,
                "attributes": get_node_attrs(node),
            }

            edges = self.application.dag.get_node_edges(node.id)
            logger.info(f"edges for this node: {len(edges)}")
            input_code = get_node_input_code_snippet(node, edges)
            output_code = get_node_output_code_snippet(node, edges)

            node_response["attributes"]["notebook_attributes"]["io"][
                "input_code"
            ] = input_code
            node_response["attributes"]["notebook_attributes"]["io"][
                "output_code"
            ] = output_code
            data.append(node_response)

        self.set_status(200)
        self.write({"data": data[0] if node_id else data})
        self.set_header("Content-Type", "application/vnd.api+json")

    # _ parameter added as post expects two arguments from route
    def post(self, _):
        """Creates a new node and runs its container
        ---
        tags: [Nodes]
        summary: Create node
        description: Create a node and run its container
        requestBody:
            description: Give an empty request body
            required: true
            content:
                application/json:
                    schema:
                        type: object
                        items:
                            NoSchema
        responses:
            200:
                description: Created node and its container id
                content:
                    application/json:
                        schema:
                            type: dict
                            items:
                                NoSchema
        """
        data = json.loads(self.request.body)
        node = MercuryNode(**data.get("attributes", {}))

        # add the node to the dag first, as this sets the jupyter port
        self.application.dag.add_node(node)

        node.initialise_container()

        data = {
            "id": node.id,
            "type": self.json_type,
            "attributes": get_node_attrs(node),
        }

        self.set_status(201)
        self.add_header("Location", f"/nodes/{node.id}")
        self.write({"data": data})
        self.set_header("Content-Type", "application/vnd.api+json")

    def patch(self, node_id):
        """Updates properties of a node
        ---
        tags: [Nodes]
        summary: Update node properties
        parameters:
          - in: path
            name: node_id
            type: string
            required: false
            description: unique node id for a specific node.
        description: Update a node in the DAG
        responses:
            200:
                description: Updated node and its container
                content:
                    application/json:
                        schema:
                            type: array
                            items:
                                NoSchema
        """
        data = json.loads(self.request.body)
        node = self.application.dag.get_node(node_id)

        node.input = data["data"].get("attributes", {}).get("input", node.input)
        node.output = data["data"].get("attributes", {}).get("output", node.output)

        data = {
            "id": node.id,
            "type": self.json_type,
            "attributes": get_node_attrs(node),
        }

        edges = self.application.dag.get_node_edges(node.id)
        input_code = get_node_input_code_snippet(node, edges)
        output_code = get_node_output_code_snippet(node, edges)
        data["attributes"]["notebook_attributes"]["io"]["input_code"] = input_code
        data["attributes"]["notebook_attributes"]["io"]["output_code"] = output_code

        self.set_status(200)
        self.write({"data": data})
        self.set_header("Content-Type", "application/vnd.api+json")

        # to do: updation for other properties

    def delete(self, node_id):
        """Deletes the node
        ---
        tags: [Nodes]
        summary: Delete node.
        parameters:
          - in: path
            name: node_id
            type: string
            required: true
            description: unique node id for a specific node.
        description: Deletes the node from the DAG
        responses:
            200:
                description: List of node(s) and their container
                content:
                    application/json:
                        schema:
                            type: array
                            items:
                                NoSchema
        """
        node = self.application.dag.get_node(node_id)
        node.mercury_container.container.kill()
        self.application.dag.remove_node(node)

        self.set_status(204)
        self.set_header("Content-Type", "application/vnd.api+json")

        # self.write({"response": [node_props]})


class NodeImageHandler(MercuryHandler):
    json_type = "nodes"

    def patch(self, node_id):
        data = json.loads(self.request.body)
        node = self.application.dag.get_node(node_id)

        assert data["data"].get("type") == "nodes"
        assert data["data"].get("id") == node_id
        assert "attributes" in data["data"]
        assert "state" in data["data"].get("attributes")

        change_state = data["data"]["attributes"]["state"]
        assert change_state in ["build"]

        if change_state == "build":
            node.commit()

        data = {
            "id": node.id,
            "type": self.json_type,
            "attributes": get_node_attrs(node),
        }

        edges = self.application.dag.get_node_edges(node.id)
        code = get_node_input_code_snippet(node, edges)
        data["attributes"]["notebook_attributes"]["io"]["input_code"] = code

        self.set_status(200)
        self.write({"data": data})
        self.set_header("Content-Type", "application/vnd.api+json")


class NodeNotebookHandler(MercuryHandler):
    json_type = "nodes"

    async def patch(self, node_id):
        data = json.loads(self.request.body)
        node = self.application.dag.get_node(node_id)

        assert data["data"].get("type") == "nodes"
        assert data["data"].get("id") == node_id
        assert "attributes" in data["data"]
        assert any(
            [
                _ in data["data"].get("attributes")
                for _ in [
                    "state",
                    "kernel_state",
                    "workflow_kernel_state",
                    "notebook_exec_exit_code",
                    "notebook_exec_pid",
                    "jupyter_server",
                ]
            ]
        )

        response_data = {
            "id": node.id,
            "type": self.json_type,
            "attributes": get_node_attrs(node),
        }

        edges = self.application.dag.get_node_edges(node.id)
        input_code = get_node_input_code_snippet(node, edges)
        output_code = get_node_output_code_snippet(node, edges)
        response_data["attributes"]["notebook_attributes"]["io"][
            "input_code"
        ] = input_code
        response_data["attributes"]["notebook_attributes"]["io"][
            "output_code"
        ] = output_code

        if "state" in data["data"]["attributes"]:

            change_state = data["data"]["attributes"]["state"]
            assert change_state in ["run", "write_json"]

            if change_state == "run":
                assert "code" in data["data"].get("attributes")
                code = data["data"]["attributes"]["code"]
                exit_code, container_output = node.execute_code(code)

            if change_state == "write_json":
                edges = self.application.dag.get_node_edges(node.id)
                container_output = "".encode()
                exit_code = -1
                if not edges:
                    logger.warning("This node does not have any edges")
                for edge in edges:
                    if edge.source_node != node:
                        continue
                    # variables that have to be written as keys in json
                    dest_inputs = [
                        _["destination"]["input"] for _ in edge.source_dest_connect
                    ]
                    # variables for which we need to get values from within the kernel
                    source_outputs = [
                        _["source"]["output"] for _ in edge.source_dest_connect
                    ]
                    logger.info(f"writing for edge {edge.id}")
                    exit_code, container_output = node.write_output_to_json(
                        source_outputs,
                        dest_inputs,
                        edge.json_path_container,
                    )

            response_data["attributes"]["notebook_attributes"][
                "container_log"
            ] = json.dumps(container_output.decode("utf-8"))
            response_data["attributes"]["notebook_attributes"]["exit_code"] = exit_code

        if "kernel_state" in data["data"]["attributes"]:
            kernel_state = data["data"]["attributes"].get("kernel_state")
            node.mercury_container.kernel_state = kernel_state
            response_data["attributes"]["notebook_attributes"][
                "kernel_state"
            ] = kernel_state

            # write to websocket here if a websocket is open and instantialised
            if node_id in KernelInfoHandler.instances:
                try:
                    logger.info(f"sending message to websocket for node {node_id}")
                    KernelInfoHandler.instances[node_id].write_message(response_data)
                except WebSocketClosedError as e:
                    logger.warning("tried writing to websocket but it is closed")

        if "workflow_kernel_state" in data["data"]["attributes"]:
            workflow_kernel_state = data["data"]["attributes"].get(
                "workflow_kernel_state"
            )
            node.mercury_container.workflow_kernel_state = workflow_kernel_state
            response_data["attributes"]["notebook_attributes"][
                "workflow_kernel_state"
            ] = workflow_kernel_state

            # write to websocket here if a websocket is open and instantialised
            if node_id in KernelInfoHandler.instances:
                try:
                    logger.info(f"sending message to websocket for node {node_id}")
                    KernelInfoHandler.instances[node_id].write_message(response_data)
                except WebSocketClosedError as e:
                    logger.warning("tried writing to websocket but it is closed")

        if "notebook_exec_exit_code" in data["data"]["attributes"]:
            exit_code = data["data"]["attributes"]["notebook_exec_exit_code"]
            node.mercury_container.notebook_exec_exit_code = exit_code
            response_data["attributes"]["notebook_attributes"][
                "notebook_exec_exit_code"
            ] = exit_code

        if "notebook_exec_pid" in data["data"]["attributes"]:
            pid = data["data"]["attributes"]["notebook_exec_pid"]
            node.mercury_container.notebook_exec_pid = pid
            response_data["attributes"]["notebook_attributes"][
                "notebook_exec_pid"
            ] = pid

        if "jupyter_server" in data["data"]["attributes"]:
            jupyter_server_state = data["data"]["attributes"]["jupyter_server"]
            node.mercury_container.jupyter_server = jupyter_server_state
            response_data["attributes"]["notebook_attributes"][
                "jupyter_server"
            ] = jupyter_server_state

            # write to websocket here if a websocket is open and instantialised
            if node_id in KernelInfoHandler.instances:
                try:
                    logger.info(f"sending message to websocket for node {node_id}")
                    KernelInfoHandler.instances[node_id].write_message(response_data)
                except WebSocketClosedError as e:
                    logger.warning("tried writing to websocket but it is closed")

        self.set_status(200)
        response_data_resource = {
            "id": node.id,
            "type": self.json_type,
            "attributes": response_data["attributes"]["notebook_attributes"],
        }
        self.write(response_data_resource)
        self.set_header("Content-Type", "application/vnd.api+json")


class KernelInfoHandler(MercuryWsHandler):
    instances = dict()
    json_type = "nodes"

    def open(self, node_id):
        if self.application.dag.get_node(node_id):
            KernelInfoHandler.instances[node_id] = self
            logger.info(f"Websocket connection opened for node {node_id}")
        else:
            self.close(code=403, reason="tried connecting to a node that doesn't exist")

    def on_close(self):
        del_node_id = self.request.uri.split("/")[2]
        if del_node_id in KernelInfoHandler.instances:
            del KernelInfoHandler.instances[del_node_id]
