import logging

from server.views import CaduceusHandler

logger = logging.getLogger(__name__)


class DagInfoHandler(CaduceusHandler):
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
