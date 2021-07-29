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

