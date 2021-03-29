import tornado.web
import json

from caduceus.node import MercuriNode


class CaduceusHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Welcome to Caduceus")


class DagInfo(tornado.web.RequestHandler):
    def get(self):
        dag_props = {
            "nodes": self.application.dag.nodes,
            "edges": self.application.dag.edges,
        }
        self.write(dag_props)


class AddNode(CaduceusHandler):
    def get(self):

        node = MercuriNode(
            input={"ai_1": "ai_1", "ai_2": "ai_2"},
            output={},
            docker_volume="/usr/src/app",
            docker_img_name="nodea",
        )
        self.application.dag.add_node(node)
        print(self.application.dag.nodes)
        self.write("Nodes: " + str(len(self.application.dag.nodes)))