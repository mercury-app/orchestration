 
FROM python:3-alpine
WORKDIR /usr/src/app

ENV di_1 ""
ENV di_2 ""

CMD paste $di_1 $di_2 | awk '{$0=$1*$2}1' > do_1