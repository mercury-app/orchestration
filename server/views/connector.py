import json
import logging
from uuid import uuid4

from mercury.edge import MercuryEdge

from server.views import MercuryHandler
from server.views.utils import get_connector_attrs

logger = logging.getLogger(__name__)


class ConnectorHandler(MercuryHandler):
    json_type = "connectors"

    def get(self, workflow_id, connector_id):

        # only work for a particular connector id for now
        assert connector_id

        connector_edge = None
        source_dest_map = None
        for _e in self.application.workflows.get(workflow_id).edges:

            for _c in _e.source_dest_connect:
                if _c["connector_id"] == connector_id:
                    connector_edge = _e
                    source_dest_map = _c
                    break
            break

        assert connector_edge, "This connector does not exist for any edge"

        data = {
            "id": source_dest_map["connector_id"],
            "type": self.json_type,
            "attributes": get_connector_attrs(connector_edge, source_dest_map),
        }

        self.set_status(200)
        self.write({"data": data})
        self.set_header("Content-Type", "application/vnd.api+json")

    def post(self, workflow_id, _):
        data = json.loads(self.request.body)

        assert data["data"].get("type") == self.json_type

        assert "attributes" in data["data"]
        attr_data = data["data"].get("attributes")

        # assert format of request
        assert "source" in attr_data
        assert "destination" in attr_data

        assert "node_id" in attr_data.get("source")
        assert "node_id" in attr_data.get("destination")

        assert workflow_id in self.application.workflows
        dag = self.application.workflows.get(workflow_id)

        source_node = dag.get_node(attr_data["source"].get("node_id"))
        dest_node = dag.get_node(attr_data["destination"].get("node_id"))

        # nodes have to exist
        assert source_node
        assert dest_node

        # some more format checking
        assert "output" in attr_data["source"]
        assert "input" in attr_data["destination"]

        # get an edge between src and destination nodes if it exists
        # otherwise create the edge

        # check if source and destination have input and output sets
        assert source_node.output
        assert dest_node.input
        assert attr_data["source"].get("output") in source_node.output
        assert attr_data["destination"].get("input") in dest_node.input

        edge = dag.get_edge_from_nodes(
            source_node_id=attr_data["source"].get("node_id"),
            destination_node_id=attr_data["destination"].get("node_id"),
        )

        if not edge:
            edge = MercuryEdge(source_node, dest_node)
            dag.add_edge(edge)

        source_dest_map = {
            "source": {"output": attr_data["source"].get("output")},
            "destination": {"input": attr_data["destination"].get("input")},
            "connector_id": uuid4().hex,
        }

        edge.source_dest_connect.append(source_dest_map)

        data = {
            "id": source_dest_map["connector_id"],
            "type": self.json_type,
            "attributes": get_connector_attrs(edge, source_dest_map),
        }

        self.set_status(201)
        self.add_header("Location", f"/connector/{source_dest_map['connector_id']}")
        self.write({"data": data})
        self.set_header("Content-Type", "application/vnd.api+json")

    def delete(self, workflow_id, connector_id):
        assert connector_id in self.application.workflows

        # only work for a particular connector id for now
        assert connector_id

        dag = self.application.workflows.get(workflow_id)
        connector_edge = None
        for _e in dag.edges:

            for del_i, _c in enumerate(_e.source_dest_connect):
                if _c["connector_id"] == connector_id:
                    connector_edge = _e
                    break
            break

        assert connector_edge, "This connector does not exist for any edge"

        connector_edge.source_dest_connect.pop(del_i)

        # Delete an edge if all connectors related to an edge
        # have been deleted
        if len(connector_edge.source_dest_connect) == 0:
            dag.remove_edge(connector_edge)

        self.set_status(204)
        self.set_header("Content-Type", "application/vnd.api+json")
