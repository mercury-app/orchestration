# Mercury Orchestration

This repository contains all the code for the service that orchestrates the
execution of workflows and underlying notebooks.

### Usage

#### Install dependencies and activate virtual environment

Install poetry - https://python-poetry.org/docs/basic-usage/

```sh
cd orchestration
poetry install
poetry shell
```

#### Start the server

```sh
python3 -m server.app
```

Go to localhost:8888

### Contributing

If you install a new dependency or update an existing dependency, commit the `poetry.lock` file as well.

### Build the docker image for Mercury

```sh
cd docker/jupyter
docker build . -t jupyter-mercury:latest
```

### API documentation

Docs in Postman
https://documenter.getpostman.com/view/2281095/TzK16F5A

[![Run in Postman](https://run.pstmn.io/button.svg)](https://app.getpostman.com/run-collection/7adb5e7a82f5292336d7)

### Triggering nodes

```python
from orchestration.node import MercuryNode
nodeA = MercuryNode(input = {"ai_1":"ai_1", "ai_2":"ai_2"}, output = {}, docker_volume="/usr/src/app", docker_img_name="nodea")
nodeA.trigger()

nodeB = MercuryNode(input = {"bi_1":"ao_1", "bi_2":"bi_2"}, output = {}, docker_volume="/usr/src/app", docker_img_name="nodeb")
nodeB.trigger()

nodeC = MercuryNode(input = {"ci_1":"ao_1", "ci_2":"ci_2"}, output = {}, docker_volume="/usr/src/app", docker_img_name="nodec")
nodeC.trigger()

nodeD = MercuryNode(input = {"di_1":"bo_1", "di_2":"co_1"}, output = {}, docker_volume="/usr/src/app", docker_img_name="noded")
nodeD.trigger()
```

```python
from orchestration.dag import MercuryDag
mercury_dag = MercuryDag()

# add two nodes and define the edge between them
mercury_dag.add_node(nodeA)
mercury_dag.add_node(nodeB)

mercury_dag.add_edge(nodeA, nodeB)


mercury_dag.add_node(nodeC)
mercury_dag.add_edge(nodeA, nodeC)

mercury_dag.add_node(nodeD)
mercury_dag.add_edge(nodeB, nodeD)
mercury_dag.add_edge(nodeC, nodeD)

mercury_dag.nx_dag.nodes
mercury_dag.nx_dag.edges
```
