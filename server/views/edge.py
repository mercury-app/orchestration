import json
import logging

from caduceus.edge import MercuriEdge

from server.views import CaduceusHandler

logger = logging.getLogger(__name__)


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
        source_dest_connect = data.get("source_dest_connect", None)

        source_dest_map = list()
        for _ in source_dest_connect:
            assert (len(_)) == 2
            source_dest_map.append({"input": _[0], "output": _[1]})

        edge = MercuriEdge(source_node, dest_node)
        edge.source_dest_connect = source_dest_map
        self.application.dag.add_edge(edge)

        edge_props = {
            "response": {
                "id": edge.id,
                "source_node": edge.source_node.id,
                "dest_node": edge.dest_node.id,
                "source_dest_connect": list(edge.source_dest_connect),
            }
        }
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
        source_dest_connect = data.get("source_dest_connect", None)

        if source_dest_connect:
            source_dest_map = list()
            for _ in source_dest_connect:
                assert (len(_)) == 2
                source_dest_map.append({"input": _[0], "output": _[1]})

            edge.source_dest_connect = source_dest_map

        edge_props = {
            "response": {
                "id": edge.id,
                "source_node": edge.source_node.id,
                "dest_node": edge.dest_node.id,
                "source_dest_connect": list(edge.source_dest_connect),
            }
        }
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
