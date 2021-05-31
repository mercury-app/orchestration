 
FROM python:3-alpine
WORKDIR /usr/src/app

ENV ai_1 ""
ENV ai_2 ""

CMD paste $ai_1 $ai_2 | awk '{$0=$1+$2}1' > ao_1