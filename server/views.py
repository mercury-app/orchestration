import tornado.web
import json

from caduceus.node import MercuriNode


class CaduceusHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Welcome to Caduceus")


class DagInfo(tornado.web.RequestHandler):
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
            print(node.__dict__)
            node_props = vars(node)
            return self.write({"response": [node_props]})
        nodes = self.application.dag.nodes
        node_props = [vars(_) for _ in nodes]
        return self.write({"response": node_props})

    # _ parameter added as post expects two arguments from route
    def post(self, _):
        data = json.loads(self.request.body)
        node = MercuriNode(**data)

        self.application.dag.add_node(node)
        print(self.application.dag.nodes)
        print("node added: ", node.id)
        self.write("Nodes: " + str(len(self.application.dag.nodes)))
