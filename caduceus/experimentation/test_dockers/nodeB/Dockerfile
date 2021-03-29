 
FROM python:3-alpine
WORKDIR /usr/src/app

ENV bi_1 ""
ENV bi_2 ""

CMD paste $bi_1 $bi_2 | awk '{$0=$1+$2}1' > bo_1