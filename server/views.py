import tornado.web
import json
import logging

from caduceus.node import MercuriNode
from caduceus.edge import MercuriEdge

logger = logging.getLogger(__name__)


class CaduceusHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Welcome to Caduceus")


class DagInfo(CaduceusHandler):
    def get(self):
        """Returns the DAG nodes and edges
        ---
        tags: [DAG]
        summary: Get dag properties.
        description: Get the nodes and edges in the DAG
        responses:
            200:
                description: List of nodes and edges in the dag
                content:
                    application/json:
                        schema:
                            type: array
                            items:
                                NoSchema
        """
        dag_props = {
            "nodes": [_.id for _ in self.application.dag.nodes],
            "edges": [
                {"edge": (_.source_node.id, _.dest_node.id), "id": _.id}
                for _ in self.application.dag.edges
            ],
        }
        self.write(dag_props)


class NodeHandler(CaduceusHandler):
    def get(self, node_id=None):
        """Returns the node(s) available
        ---
        tags: [Nodes]
        summary: Get nodes.
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
                "container": {
                    "container_id": _.caduceus_container.container_id,
                    "container_state": _.caduceus_container.container_state,
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
            }
        }
        self.write(response)

    def put(self, node_id):
        """Updates properties of a node
        ---
        tags: [Nodes]
        summary: Update node properties
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
        node.docker_img_name = data.get("docker_img_name", node.docker_img_name)

        node_props = {
            "id": node.id,
            "container": {
                "container_id": node.caduceus_container.container_id,
                "container_state": node.caduceus_container.container_state,
            },
        }
        self.write({"response": [node_props]})

        # to do: updation for other properties

    def delete(self, node_id):
        """Deletes the node
        ---
        tags: [Nodes]
        summary: Delete node.
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
            assert "image_name" in data.keys()
            img_name = data.get("image_name")
            img_tag = data.get("image_tag", "latest")
            node.caduceus_container.commit(img_name, img_tag)

        response = {
            "id": node.id,
            "container": {
                "container_id": node.caduceus_container.container_id,
                "container_state": node.caduceus_container.container_state,
            },
        }

        self.write({"response": response})


class EdgeHandler(CaduceusHandler):
    def get(self, edge_id):
        """Returns the edge(s) available
        ---
        tags: [Edges]
        summary: Get edges.
        description: Get the edges in the DAG
        responses:
            200:
                description: List of edges(s) and their source and destination nodes
                content:
                    application/json:
                        schema:
                            type: array
                            items:
                                NoSchema
        """
        if edge_id:
            edge = self.application.dag.get_edge(edge_id)
            edges = [edge]
        else:
            edges = self.application.dag.edges

        print(edges)
        edge_props = [
            {
                "id": _.id,
                "source_node": _.source_node.id,
                "dest_node": _.dest_node.id,
                "source_dest_connect": list(_.source_dest_connect),
            }
            for _ in edges
        ]
        return self.write({"response": edge_props})

    def post(self, _):
        """Creates a new edge
        ---
        tags: [Edges]
        summary: Create edge
        description: Create a new edge between existing nodes in the DAG
        responses:
            200:
                description: Created edge properties
                content:
                    application/json:
                        schema:
                            type: array
                            items:
                                NoSchema
        """
        data = json.loads(self.request.body)

        source_node = self.application.dag.get_node(data.get("source_node", None))
        dest_node = self.application.dag.get_node(data.get("dest_node", None))
        source_dest_connect = data.get("source_dest_connect", set())

        edge = MercuriEdge(source_node, dest_node, source_dest_connect)
        self.application.dag.add_edge(edge)

        edge_props = {"response": {"id": edge.id}}
        self.write(edge_props)

    def put(self, edge_id):
        """Modify the edge
        ---
        tags: [Edges]
        summary: Modify edge.
        description: Modify the edge in the DAG
        responses:
            200:
                description: Modified edge properties
                content:
                    application/json:
                        schema:
                            type: array
                            items:
                                NoSchema
        """
        data = json.loads(self.request.body)
        edge = self.application.dag.get_edge(edge_id)

        edge.source_node = data.get("source_node", edge.source_node)
        edge.dest_node = data.get("dest_node", edge.source_node)
        edge.source_dest_connect = data.get(
            "source_dest_connect", edge.source_dest_connect
        )

        self.source_dest_connect = data.get(
            "source_dest_connect", edge.source_dest_connect
        )

        edge_props = {"response": {"id": edge.id}}
        self.write({"response": [edge_props]})

    def delete(self, edge_id):
        """Delete the edge
        ---
        tags: [Edges]
        summary: Delete edge.
        description: Delete the edge in the DAG
        responses:
            200:
                description: Deleted edge and its properties
                content:
                    application/json:
                        schema:
                            type: array
                            items:
                                NoSchema
        """
        edge = self.application.dag.get_edge(edge_id)
        self.application.dag.remove_edge(edge)

        edge_props = {"response": {"id": edge.id}}
        self.write({"response": [edge_props]})
