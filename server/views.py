import tornado.web
import json

from caduceus.node import MercuriNode
from caduceus.edge import MercuriEdge


class CaduceusHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Welcome to Caduceus")


class DagInfo(CaduceusHandler):
    def get(self):
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
        data = json.loads(self.request.body)
        print("data", data)
        node = self.application.dag.get_node(node_id)

        node.input = data.get("input", node.input)
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
    def put(self, node_id):
        print("triggered put")
        data = json.loads(self.request.body)
        node = self.application.dag.get_node(node_id)

        trigger = data.get("status", None)

        if trigger == "run":
            print("triggering node")
            container_id = node.trigger()

        response = {"response": {"container": {"id": container_id}}}

        return response


class EdgeHandler(CaduceusHandler):
    def get(self, edge_id):
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
        data = json.loads(self.request.body)

        source_node = self.application.dag.get_node(data.get("source_node", None))
        dest_node = self.application.dag.get_node(data.get("dest_node", None))
        source_dest_connect = data.get("source_dest_connect", set())

        edge = MercuriEdge(source_node, dest_node, source_dest_connect)
        self.application.dag.add_edge(edge)

        edge_props = {"response": {"id": edge.id}}
        self.write(edge_props)

    def put(self, edge_id):
        data = json.loads(self.request.body)
        edge = self.application.dag.get_edge(edge_id)

        edge.source_node = data.get("source_node", edge.source_node)
        edge.dest_node = data.get("dest_node", edge.source_node)
        edge.source_dest_connect = data.get(
            "source_dest_connect", edge.source_dest_connect
        )

        edge_props = {"response": {"id": edge.id}}
        self.write({"response": [edge_props]})

    def delete(self, edge_id):
        edge = self.application.dag.get_edge(edge_id)
        self.application.dag.remove_edge(edge)

        edge_props = {"response": {"id": edge.id}}
        self.write({"response": [edge_props]})
