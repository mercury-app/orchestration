
### Create some dummy dockers and some dummy files
```
cd orchestrator/experimentation
./build_test_dockers.sh 
```

```
tree experimentation/
```
experimentation/
├── build_test_dockers.sh
├── common_volume
│   ├── ai_1
│   ├── ai_2
│   ├── bi_2
│   ├── ci_2


### Triggering nodes

```
>>> from orchestrator.node import MercuriNode
>>> nodeA = MercuriNode(input = {"ai_1":"ai_1", "ai_2":"ai_2"}, output = {}, docker_volume="/usr/src/app", docker_img_name="nodea")
>>> nodeA.trigger()

>>> nodeB = MercuriNode(input = {"bi_1":"ao_1", "bi_2":"bi_2"}, output = {}, docker_volume="/usr/src/app", docker_img_name="nodeb")
>>> nodeB.trigger()

>>> nodeC = MercuriNode(input = {"ci_1":"ao_1", "ci_2":"ci_2"}, output = {}, docker_volume="/usr/src/app", docker_img_name="nodec")
>>> nodeC.trigger()

>>> nodeD = MercuriNode(input = {"di_1":"bo_1", "di_2":"co_1"}, output = {}, docker_volume="/usr/src/app", docker_img_name="noded")
>>> nodeD.trigger()
```