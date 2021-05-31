 
FROM python:3-alpine
WORKDIR /usr/src/app

ENV ci_1 ""
ENV ci_2 ""

CMD paste $ci_1 $ci_2 | awk '{$0=$1+$2}1' > co_1