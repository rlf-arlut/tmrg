#!/bin/bash
python3 -m venv venv
. venv/bin/activate
pip install --upgrade pip
pip install pytest pytest-cov
pip install -e .  # install tmrg
