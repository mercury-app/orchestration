import logging

from server.views import CaduceusHandler

logger = logging.getLogger(__name__)


class WorkflowHandler(CaduceusHandler):
    json_type = "workflow"

    def get(self):
        data = {
            "id": self.application.dag.id,
            "type": self.json_type,
            "attributes": {
                "nodes": [_.id for _ in self.application.dag.nodes],
                "edges": [
                    {"edge": (_.source_node.id, _.dest_node.id), "id": _.id}
                    for _ in self.application.dag.edges
                ],
            }
        }

        self.set_status(200)
        self.write({"data": data})
        self.set_header("Content-Type", "application/vnd.api+json")
