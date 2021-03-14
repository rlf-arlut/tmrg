#!/bin/bash
docker build --no-cache -t gitlab-registry.cern.ch/tmrg/tmrg -f tmrg_ubuntu20.dockerfile . && docker push gitlab-registry.cern.ch/tmrg/tmrg_ubuntu20
