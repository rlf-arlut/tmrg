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

# Taken from https://github.com/chipsalliance/verible/releases/tag/v0.0-1316-g94f5d01
# The ubuntu 20.04 version was downloaded for this image

ADD verible-v0.0-1316-g94f5d01_u2004/bin/verible-verilog-format /usr/sbin/verible-verilog-format
ADD verible-v0.0-1316-g94f5d01_u2004/bin/verible-verilog-lint /usr/sbin/verible-verilog-lint
ADD verible-v0.0-1316-g94f5d01_u2004/bin/verible-verilog-syntax /usr/sbin/verible-verilog-syntax
