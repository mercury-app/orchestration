from typing import List

from mercury.node import MercuryNode
from mercury.edge import MercuryEdge
from mercury.dag import MercuryDag


def get_node_input_code_snippet(node: MercuryNode, edges: List[MercuryEdge]) -> str:

    code_lines = []
    inputs_available_in_json = []
    for edge in edges:
        snippet = edge.get_input_code_snippet()
        if not snippet:
            continue
        inputs_available_in_json += edge.json_inputs
        snippet += f"\nfrom source node {edge.source_node.id}\n"
        code_lines.append(snippet)

    code_lines = []
    if node.input:
        for input_name in node.input:
            # to do: check kernel type running in container
            if input_name not in inputs_available_in_json:
                snippet = f"{input_name} = None\n"
                code_lines.append(snippet)

    code = "\n".join(code_lines)
    code = "# Mercury-Input\n" + code
    return code


def get_node_output_code_snippet(node: MercuryNode, edges: List[MercuryEdge]) -> str:
    code_lines = []
    for edge in edges:
        snippet = edge.get_output_code_snippet()
        snippet += f"\nfor destination node {edge.dest_node.id}\n"
        code_lines.append(snippet)

    code = "\n".join(code_lines)
    code = "# Mercury-Output\n" + code
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
            "io": {"input_code": None, "output_code": None},
        },
    }
