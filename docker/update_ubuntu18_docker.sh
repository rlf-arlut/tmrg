#!/bin/bash
docker build --no-cache -t gitlab-registry.cern.ch/tmrg/tmrg/tmrg_ubuntu18 -f tmrg_ubuntu18.dockerfile . && docker push gitlab-registry.cern.ch/tmrg/tmrg/tmrg_ubuntu18
