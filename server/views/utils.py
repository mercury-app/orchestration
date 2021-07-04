from typing import List
import logging

from mercury.node import MercuryNode
from mercury.edge import MercuryEdge
from mercury.dag import MercuryDag

logger = logging.getLogger(__name__)

OUTPUT_CODE_SNIPPET_HEADER = "# Mercury-Output\n"
INPUT_CODE_SNIPPET_HEADER = "# Mercury-Input\n"


def get_node_input_code_snippet(node: MercuryNode, edges: List[MercuryEdge]) -> str:

    code_lines = []
    inputs_available_in_json = []
    for edge in edges:
        if edge.dest_node != node:
            continue
        snippet = edge.get_input_code_snippet()
        if not snippet:
            continue
        snippet = f"\n#from source node {edge.source_node.id}\n" + snippet + "\n"
        inputs_available_in_json += edge.json_inputs
        code_lines.append(snippet)

    if node.input:
        for input_name in node.input:
            # to do: check kernel type running in container
            if input_name not in inputs_available_in_json:
                snippet = f"{input_name} = None\n"
                code_lines.append(snippet)

    code = "".join(code_lines)
    code = INPUT_CODE_SNIPPET_HEADER + code
    return code


def get_node_output_code_snippet(node: MercuryNode, edges: List[MercuryEdge]) -> str:
    code_lines = []
    for edge in edges:
        if edge.source_node != node:
            continue
        snippet = edge.get_output_code_snippet()
        snippet = f"\n# for destination node {edge.dest_node.id}\n" + snippet
        code_lines.append(snippet)

    if len(code_lines) == 0:
        code_lines.append("# Create a connector for this node to export outputs")

    code = "".join(code_lines)
    code = OUTPUT_CODE_SNIPPET_HEADER + code
    return code


def get_node_attrs(node: MercuryNode) -> dict:
    return {
        "input": node.input,
        "output": node.output,
        "image_attributes": {
            "name": node.docker_img_name,
            "tag": node.docker_img_tag,
            "state": None,
        },
        "container_attributes": {
            "id": node.mercury_container.container_id,
            "state": node.mercury_container.container_state["Status"],
        },
        "notebook_attributes": {
            "url": f"http://localhost:{node.jupyter_port}/notebooks/work/scripts/Untitled.ipynb?kernel_name=python3",
            "state": None,
            "exit_code": -1,
            "container_log": None,
            "kernel_state": node.mercury_container.kernel_state,
            "workflow_kernel_state": node.mercury_container.workflow_kernel_state,
            "jupyter_server": node.mercury_container.jupyter_server,
            "notebook_exec_exit_code": node.mercury_container.notebook_exec_exit_code,
            "io": {"input_code": None, "output_code": None},
        },
    }


def get_workflow_attrs(dag: MercuryDag) -> dict:
    nodes = [{"id": node.id, "type": "nodes"} for node in dag.nodes]

    connectors = []
    for _e in dag.edges:
        for _c in _e.source_dest_connect:
            connector = {
                "id": _c["connector_id"],
                "type": "connectors",
            }
            connectors.append(connector)

    valid_connections = dag.get_valid_connections_for_nodes()
    valid_connections = {
        src.id: [dest.id for dest in valid_connections.get(src)]
        for src in valid_connections
    }

    attrs_data = {
        "nodes": nodes,
        "connectors": connectors,
        "valid_connections": valid_connections,
        "run_exit_code": -1,
    }
    return attrs_data
