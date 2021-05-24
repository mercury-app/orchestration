import logging

from server.views import CaduceusHandler

logger = logging.getLogger(__name__)


class WorkflowHandler(CaduceusHandler):
    json_type = "workflow"

    def get(self):
        valid_destinations = self.application.dag.get_valid_destinations_for_nodes()
        data = {
            "id": self.application.dag.id,
            "type": self.json_type,
            "attributes": {
                "nodes": [
                    {
                        "id": node.id,
                        "valid_destinations": [
                            dest.id for dest in valid_destinations.get(node)
                        ],
                    }
                    for node in self.application.dag.nodes
                ],
                "edges": [
                    {"edge": (edge.source_node.id, edge.dest_node.id), "id": edge.id}
                    for edge in self.application.dag.edges
                ],
            },
        }

        self.set_status(200)
        self.write({"data": data})
        self.set_header("Content-Type", "application/vnd.api+json")
