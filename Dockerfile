FROM python:3.7

RUN curl -s http://ip-api.com | grep China > /dev/null && \
    curl -s http://mirrors.163.com/.help/sources.list.jessie > /etc/apt/sources.list || true

RUN apt-get update;\
    apt-get install -y vim gettext;\
    true

COPY ./requirements.txt /opt/examples/
WORKDIR /opt/examples

RUN curl -s http://ip-api.com | grep China > /dev/null && \
    pip install -r requirements.txt -i https://pypi.doubanio.com/simple --trusted-host pypi.doubanio.com || \
    pip install -r requirements.txt
