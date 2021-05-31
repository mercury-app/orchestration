import logging

from server.views import MercuryHandler
from server.views.node import NodeHandler
from server.views.connector import ConnectorHandler

logger = logging.getLogger(__name__)


class WorkflowHandler(MercuryHandler):
    json_type = "workflows"

    def get(self):
        nodes = [
            {"id": node.id, "type": NodeHandler.json_type}
            for node in self.application.dag.nodes
        ]

        connectors = []
        for _e in self.application.dag.edges:
            for _c in _e.source_dest_connect:
                connector = {
                    "id": _c["connector_id"],
                    "type": ConnectorHandler.json_type,
                }
                connectors.append(connector)

        valid_connections = self.application.dag.get_valid_connections_for_nodes()
        valid_connections = {
            src.id: [dest.id for dest in valid_connections.get(src)]
            for src in valid_connections
        }
        data = {
            "id": self.application.dag.id,
            "type": self.json_type,
            "attributes": {
                "nodes": nodes,
                "connectors": connectors,
                "valid_connections": valid_connections,
            },
        }

        self.set_status(200)
        self.write({"data": [data]})
        self.set_header("Content-Type", "application/vnd.api+json")
