FROM ubuntu:18.04

MAINTAINER Szymon Kulis <szymon.kulis@gmail.com>

RUN apt-get update -y
RUN DEBIAN_FRONTEND="noninteractive" apt-get -y install iverilog python make git inkscape python3-venv virtualenv

