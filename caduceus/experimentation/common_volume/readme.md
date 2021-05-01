docker run -e ai_1=ai_1 -e ai_2=ai_2  -v $(pwd):/usr/src/app nodea:latest 

docker run -e bi_1=ao_1 -e bi_2=bi_2 -v $(pwd):/usr/src/app nodeb:latest

docker run -e ci_1=ao_1 -e ci_2=ci_2 -v $(pwd):/usr/src/app nodec:latest

docker run -e di_1=bo_1 -e di_2=co_1 -v $(pwd):/usr/src/app noded:latest 