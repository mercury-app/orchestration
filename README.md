# Caduceus


### Start the server
```
cd caduceus
python3 -m server.app
```

Go to localhost:8888


### Create some dummy dockers and some dummy files
```
cd caduceus/experimentation
./build_test_dockers.sh 
```

```
tree experimentation/
```

```
experimentation/
├── build_test_dockers.sh
├── common_volume
│   ├── ai_1
│   ├── ai_2
│   ├── bi_2
│   ├── ci_2
```

### Triggering nodes

```
from caduceus.node import MercuriNode
nodeA = MercuriNode(input = {"ai_1":"ai_1", "ai_2":"ai_2"}, output = {}, docker_volume="/usr/src/app", docker_img_name="nodea")
nodeA.trigger()

nodeB = MercuriNode(input = {"bi_1":"ao_1", "bi_2":"bi_2"}, output = {}, docker_volume="/usr/src/app", docker_img_name="nodeb")
nodeB.trigger()

nodeC = MercuriNode(input = {"ci_1":"ao_1", "ci_2":"ci_2"}, output = {}, docker_volume="/usr/src/app", docker_img_name="nodec")
nodeC.trigger()

nodeD = MercuriNode(input = {"di_1":"bo_1", "di_2":"co_1"}, output = {}, docker_volume="/usr/src/app", docker_img_name="noded")
nodeD.trigger()
```

```
from caduceus.dag import MercuriDag
mercuri_dag = MercuriDag()

# add two nodes and define the edge between them
mercuri_dag.add_node(nodeA)
mercuri_dag.add_node(nodeB)

mercuri_dag.add_edge(nodeA, nodeB)


mercuri_dag.add_node(nodeC)
mercuri_dag.add_edge(nodeA, nodeC)

mercuri_dag.add_node(nodeD)
mercuri_dag.add_edge(nodeB, nodeD)
mercuri_dag.add_edge(nodeC, nodeD)

mercuri_dag.nx_dag.nodes
mercuri_dag.nx_dag.edges
```