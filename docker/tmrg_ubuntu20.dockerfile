FROM ubuntu:20.04

MAINTAINER Szymon Kulis <szymon.kulis@gmail.com>

RUN apt-get update -y
RUN DEBIAN_FRONTEND="noninteractive" apt-get -y install python git python3-pip python3-dev python3-venv autoconf g++ gperf flex bison build-essential
RUN DEBIAN_FRONTEND="noninteractive" git clone https://github.com/steveicarus/iverilog.git
RUN DEBIAN_FRONTEND="noninteractive" cd iverilog &&\
                                       sh autoconf.sh &&\
                                       sh ./configure &&\
                                       make -j8 &&\
                                       make install

RUN DEBIAN_FRONTEND="noninteractive" cd /usr/local/bin &&\
                                       ln -s /usr/bin/python3 python &&\
                                       pip3 install --upgrade pip
