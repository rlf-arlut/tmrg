FROM ubuntu:20.04

MAINTAINER Szymon Kulis <szymon.kulis@gmail.com>

RUN apt-get update -y
RUN DEBIAN_FRONTEND="noninteractive" apt-get -y install iverilog python git python3-pip python3-dev python3-venv \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip3 install --upgrade pip
