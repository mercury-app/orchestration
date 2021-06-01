import json
import logging

from mercury.node import MercuryNode

from server.views import MercuryHandler
from server.views.utils import get_node_attrs

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

        data = [
            {"id": _.id, "type": self.json_type, "attributes": get_node_attrs(_)}
            for _ in nodes
        ]

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


class NodeContainerHandler(MercuryHandler):
    def post(self, node_id):
        print("triggered put", node_id)
        data = json.loads(self.request.body)
        node = self.application.dag.get_node(node_id)

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

        self.set_status(200)
        self.write({"data": data})
        self.set_header("Content-Type", "application/vnd.api+json")
