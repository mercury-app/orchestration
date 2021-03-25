#!/bin/bash

# build 4 docker nodes
cd test_dockers/nodeA && ./build.sh && cd -
cd test_dockers/nodeB && ./build.sh && cd -
cd test_dockers/nodeC && ./build.sh && cd -
cd test_dockers/nodeD && ./build.sh && cd -


# create some dummy files for input to nodes
mkdir common_volume/
cd common_volume/
echo "1
2" > ai_1
echo "2
4" > ai_2
echo
echo "12
21" > bi_2
echo "19
33" > ci_2
cd -
