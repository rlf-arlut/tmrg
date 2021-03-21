#!/bin/bash
PYTHON_VERSION=$(python -c 'import sys; print(sys.version_info[0])')

if [ $PYTHON_VERSION == 3 ]; then
  python3 -m venv venv
else
  virtualenv venv
fi
. venv/bin/activate
pip install --upgrade pip
pip install pytest pytest-cov
pip install -e .  # install tmrg
