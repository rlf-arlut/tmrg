#!/bin/bash
docker build --no-cache -t gitlab-registry.cern.ch/tmrg/tmrg -f Dockerfile . && docker push gitlab-registry.cern.ch/tmrg/tmrg
