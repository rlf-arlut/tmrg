FROM ubuntu:18.04

MAINTAINER Szymon Kulis <szymon.kulis@gmail.com>

RUN apt-get update -y
RUN DEBIAN_FRONTEND="noninteractive" apt-get -y install python make git python3-venv virtualenv autoconf g++ gperf flex bison build-essential

RUN DEBIAN_FRONTEND="noninteractive" git clone https://github.com/steveicarus/iverilog.git
RUN DEBIAN_FRONTEND="noninteractive" cd iverilog &&\
                                       sh autoconf.sh &&\
                                       sh ./configure &&\
                                       make -j8 &&\
                                       make install

# Taken from https://github.com/chipsalliance/verible/releases/tag/v0.0-1316-g94f5d01
# The ubuntu 18.04 version was downloaded for this image

ADD verible-v0.0-1316-g94f5d01_u1804/bin/verible-verilog-format /usr/sbin/verible-verilog-format
ADD verible-v0.0-1316-g94f5d01_u1804/bin/verible-verilog-lint /usr/sbin/verible-verilog-lint
ADD verible-v0.0-1316-g94f5d01_u1804/bin/verible-verilog-syntax /usr/sbin/verible-verilog-syntax
