#!/bin/bash
docker build --no-cache -t gitlab-registry.cern.ch/skulis/tmrg -f Dockerfile . && docker push gitlab-registry.cern.ch/skulis/tmrg
