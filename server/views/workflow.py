import logging
import json

from server.views import MercuryHandler
from server.views.utils import get_workflow_attrs

logger = logging.getLogger(__name__)


class WorkflowHandler(MercuryHandler):
    json_type = "workflows"

    def get(self, workflow_id=None):
        data = {
            "id": self.application.dag.id,
            "type": self.json_type,
            "attributes": get_workflow_attrs(self.application.dag),
        }

        self.set_status(200)
        self.write({"data": [data]})
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
