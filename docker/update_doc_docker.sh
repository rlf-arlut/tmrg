#!/bin/bash
docker build --no-cache -t gitlab-registry.cern.ch/tmrg/tmrg/tmrg_doc -f tmrg_doc.dockerfile . && docker push gitlab-registry.cern.ch/tmrg/tmrg/tmrg_doc
