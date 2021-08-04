FROM ubuntu:20.10

WORKDIR /home/ubuntu/app

COPY requirements.txt requirements.txt

RUN apt-get update

RUN apt-get install -y apt-utils python3 python3-pip

RUN pip3 install -r requirements.txt
