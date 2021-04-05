import tornado.web
import json

from caduceus.node import MercuriNode


class CaduceusHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Welcome to Caduceus")


class DagInfo(CaduceusHandler):
    def get(self):
        dag_props = {
            "nodes": [str(_) for _ in self.application.dag.nodes],
            "edges": [str(_) for _ in self.application.dag.edges],
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

        node_props = vars(node)
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


class TriggerNode(CaduceusHandler):
    def put(self, node_id):
        print("triggered put")
        data = json.loads(self.request.body)
        node = self.application.dag.get_node(node_id)

        trigger = data.get("status", None)

        if trigger == "run":
            print("triggering node")
            container_id = await node.trigger()

        response = {"response": {"container": {"id": container_id}}}

        return response
