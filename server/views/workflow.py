import json
import logging

from mercury.node import MercuryNode
from mercury.dag import MercuryDag
from mercury.edge import MercuryEdge

from server.views import MercuryHandler
from server.views.node import NodeHandler
from server.views.connector import ConnectorHandler
from server.views.utils import get_workflow_attrs, get_node_attrs, get_connector_attrs

logger = logging.getLogger(__name__)


class WorkflowHandler(MercuryHandler):
    json_type = "workflows"

    def _workflow_data_from_dag(self, dag):
        if dag is None:
            return {}

        nodes = [
            {
                "id": node.id,
                "type": NodeHandler.json_type,
                "attributes": get_node_attrs(node),
            }
            for node in dag.nodes
        ]

        connectors = []
        for _e in dag.edges:
            for _c in _e.source_dest_connect:
                connector = {
                    "id": _c["connector_id"],
                    "type": ConnectorHandler.json_type,
                    "attributes": get_connector_attrs(_e, _c),
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
            "attributes": get_workflow_attrs(dag),
        }
        return data

    def _dag_from_workflow_data(self, workflow_data, dag_id=None):
        # When we restore an existing workflow, all the containers being used by current
        # workflows must be stopped. Otherwise there is a chance of their port mappings
        # colliding with each other and ports of existing containers cannot be changed.
        from mercury.docker_client import docker_cl

        logger.info("Killing already running containers...")
        [
            _.kill()
            for _ in docker_cl.containers.list()
            if "jupyter-mercury:latest" in _.image.tags
        ]

        logger.info("Restoring a workflow...")
        notebooks_dir = workflow_data.get("attributes").get("notebooks_dir")
        port_range = workflow_data.get("attributes").get("port_range")
        dag = MercuryDag(dag_id, notebooks_dir, port_range)

        nodes_data = workflow_data.get("attributes").get("nodes")
        for node_data in nodes_data:
            node_id = node_data.get("id")
            node_attributes = node_data.get("attributes")
            node = MercuryNode(
                node_attributes.get("name"),
                node_id,
                node_attributes.get("input"),
                node_attributes.get("output"),
                node_attributes.get("image_attributes").get("name"),
                node_attributes.get("image_attributes").get("tag"),
                container_id=node_attributes.get("container_attributes").get("id"),
            )
            dag.add_node(node)
            if node.mercury_container is not None:
                node.restart_container()
            else:
                node.initialise_container()

        connectors_data = workflow_data.get("attributes").get("connectors")
        for connector_data in connectors_data:
            connector_attributes = connector_data.get("attributes")
            source = connector_attributes.get("source")
            dest = connector_attributes.get("destination")
            source_node = dag.get_node(source.get("node_id"))
            dest_node = dag.get_node(dest.get("node_id"))

            # nodes should have already been created
            assert source_node is not None
            assert dest_node is not None

            edge = dag.get_edge_from_nodes(
                source_node_id=source.get("node_id"),
                destination_node_id=dest.get("node_id"),
            )
            if not edge:
                edge = MercuryEdge(source_node, dest_node)
                dag.add_edge(edge)

            source_dest_map = {
                "source": {"output": source.get("output")},
                "destination": {"input": dest.get("input")},
                "connector_id": connector_data.get("id"),
            }
            edge.source_dest_connect.append(source_dest_map)

        return dag

    def get(self, workflow_id=None):
        data = None
        if workflow_id is None:
            data = [
                self._workflow_data_from_dag(dag)
                for dag in self.application.workflows.values()
            ]
        else:
            dag = self.application.workflows.get(workflow_id)
            if dag is None:
                self.set_status(404)
                self.write("Workflow not found")
                return

            data = self._workflow_data_from_dag(dag)

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

        dag_id = data.get("id")
        if "attributes" in data and "nodes" in data.get("attributes"):
            dag = self._dag_from_workflow_data(data, dag_id)
        else:
            notebooks_dir = data.get("attributes").get("notebooks_dir")
            port_range = data.get("attributes").get("port_range")
            dag = MercuryDag(dag_id, notebooks_dir, port_range)

        self.application.workflows[dag.id] = dag
        data = self._workflow_data_from_dag(dag)

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

    def delete(self, workflow_id):
        assert workflow_id in self.application.workflows

        dag: MercuryDag = self.application.workflows.get(workflow_id)
        for edge in dag.edges:
            dag.remove_edge(edge)
        for node in dag.nodes:
            node.mercury_container.container.kill()
            dag.remove_node(node)
        self.application.workflows.pop(workflow_id)

        self.set_status(204)
        self.set_header("Content-Type", "application/vnd.api+json")
