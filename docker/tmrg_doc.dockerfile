FROM ubuntu:18.04

MAINTAINER Szymon Kulis <szymon.kulis@gmail.com>

RUN apt-get update -y
RUN DEBIAN_FRONTEND="noninteractive" apt-get -y install python-coverage sphinx-common make texlive-latex-base texlive-latex-recommended texlive-fonts-recommended texlive-latex-extra git inkscape latexmk

