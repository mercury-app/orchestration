from mercury.node import MercuryNode
from mercury.edge import MercuryEdge


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
            "id": node.caduceus_container.container_id,
            "state": node.caduceus_container.container_state["Status"],
        },
        "notebook_attributes": {
            "url": f"http://localhost:{node.jupyter_port}/notebooks/work/scripts/Untitled.ipynb?kernel_name=python3",
            "state": None,
            "exit_code": -1,
        },
    }
