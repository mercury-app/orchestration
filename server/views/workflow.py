import json
import logging
from mercury.dag import MercuryDag

from server.views import MercuryHandler
from server.views.utils import get_workflow_attrs

logger = logging.getLogger(__name__)


class WorkflowHandler(MercuryHandler):
    json_type = "workflows"

    def _data_for_id(self, workflow_id):
        dag = self.application.workflows.get(workflow_id)
        if dag is None:
            return {}

        nodes = [{"id": node.id, "type": NodeHandler.json_type} for node in dag.nodes]

        connectors = []
        for _e in dag.edges:
            for _c in _e.source_dest_connect:
                connector = {
                    "id": _c["connector_id"],
                    "type": ConnectorHandler.json_type,
                }
                connectors.append(connector)

        valid_connections = dag.get_valid_connections_for_nodes()
        valid_connections = {
            src.id: [dest.id for dest in valid_connections.get(src)]
            for src in valid_connections
        }

        data = {
            "id": dag.id,
            "type": self.json_type,
            "attributes": get_workflow_attrs(self.application.dag),
        }
        return data

    def get(self, workflow_id=None):
        data = None
        if workflow_id is None:
            data = [
                self._data_for_id(workflow_id)
                for workflow_id in self.application.workflows
            ]
        else:
            data = self._data_for_id(workflow_id)

        self.set_status(200)
        self.write({"data": data})
        self.set_header("Content-Type", "application/vnd.api+json")

    # _ parameter added as post expects two arguments from route
    def post(self, _):
        body = json.loads(self.request.body)
        data = body.get("data")
        data_type = data.get("type", "")
        if data_type != "workflows":
            self.set_status(409)
            self.write("Unrecognized resource type")
            return

        # add the node to the dag first, as this sets the jupyter port
        dag = MercuryDag()
        self.application.workflows[dag.id] = dag

        data = self._data_for_id(dag.id)

        self.set_status(201)
        self.add_header("Location", f"/workflows/{dag.id}")
        self.write({"data": data})
        self.set_header("Content-Type", "application/vnd.api+json")

    async def patch(self, workflow_id):
        data = json.loads(self.request.body)

        assert data["data"].get("type") == "workflows"
        assert data["data"].get("id") == workflow_id
        assert "attributes" in data["data"]
        assert "state" in data["data"].get("attributes")

        assert data["data"]["attributes"]["state"] in ["run", "stop"]

        if data["data"]["attributes"]["state"] == "run":
            self.application.dag.state = "running"
            exit_code = await self.application.dag.run_dag()
            self.application.dag.state = None

        if data["data"]["attributes"]["state"] == "stop":
            logger.info("received stop signal")
            self.application.dag.state = "stop"
            exit_code = 1

        response = {
            "id": self.application.dag.id,
            "type": self.json_type,
            "attributes": get_workflow_attrs(self.application.dag),
        }
        response["attributes"]["run_exit_code"] = exit_code
        self.write({"data": response})
        self.set_header("Content-Type", "application/vnd.api+json")
