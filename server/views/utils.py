from caduceus.node import MercuriNode
from caduceus.edge import MercuriEdge


def get_node_attrs(node: MercuriNode) -> dict:
    return {
        "input": node.input,
        "output": node.output,
        "docker_img_name": node.docker_img_name,
        "docker_img_tag": node.docker_img_tag,
        "container_id": node.caduceus_container.container_id,
        "container_state": node.caduceus_container.container_state,
        "notebook_url": f"http://localhost:{node.jupyter_port}/notebooks/work/scripts/Untitled.ipynb?kernel_name=python3",
    }


def get_edge_attrs(edge: MercuriEdge) -> dict:
    return {}
