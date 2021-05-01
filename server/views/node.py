import json
import logging

from caduceus.node import MercuriNode

from server.views import CaduceusHandler

logger = logging.getLogger(__name__)

JUPYTER_PORT = "8888"


class NodeHandler(CaduceusHandler):
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

        node_props = [
            {
                "id": _.id,
                "input": _.input,
                "output": _.output,
                "docker_img_name": _.docker_img_name,
                "docker_img_tag": _.docker_img_tag,
                "container": {
                    "container_id": _.caduceus_container.container_id,
                    "container_state": _.caduceus_container.container_state,
                    "notebook_url": f"http://localhost:{JUPYTER_PORT}/notebooks/Untitled.ipynb?kernel_name=python3",
                },
            }
            for _ in nodes
        ]
        return self.write({"response": node_props})

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
        node = MercuriNode(**data)
        node.initialise_container()
        self.application.dag.add_node(node)

        response = {
            "response": {
                "id": node.id,
                "container_id": node.caduceus_container.container_id,
                "notebook_url": f"http://localhost:{JUPYTER_PORT}/notebooks/Untitled.ipynb?kernel_name=python3",
            }
        }
        self.write(response)

    def put(self, node_id):
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
        print("data", data)
        node = self.application.dag.get_node(node_id)

        node.input = data.get("input", node.input)
        node.output = data.get("output", node.output)

        node_props = {
            "id": node.id,
            "container": {
                "container_id": node.caduceus_container.container_id,
                "container_state": node.caduceus_container.container_state,
                "notebook_url": f"http://localhost:{JUPYTER_PORT}/notebooks/Untitled.ipynb?kernel_name=python3",
            },
        }
        self.write({"response": [node_props]})

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
        self.application.dag.remove_node(node)

        node_props = {
            "id": node.id,
            "container": {
                "container_id": node.caduceus_container.container_id,
                "container_state": node.caduceus_container.container_state,
            },
        }
        self.write({"response": [node_props]})


class NodeContainerHandler(CaduceusHandler):
    def post(self, node_id):
        print("triggered put", node_id)
        data = json.loads(self.request.body)
        node = self.application.dag.get_node(node_id)

        container_cmd = data.get("status", None)

        if container_cmd == "run":
            exit_code, output = node.run()
            logger.info(f"Exit code: {exit_code}")
            logger.info(f"Output: {output}")

        if container_cmd == "commit":
            node.commit()

        response = {
            "id": node.id,
            "container": {
                "container_id": node.caduceus_container.container_id,
                "container_state": node.caduceus_container.container_state,
            },
            "docker_img_name": node.docker_img_name,
            "docker_img_tag": node.docker_img_tag,
        }

        self.write({"response": response})
