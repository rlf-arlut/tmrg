#!/bin/bash
PYTHON_VERSION=$(python -c 'import sys; print(sys.version_info[0])')
echo "${PYTHON_VERSION}"
if [$PYTHON_VERSION -eq 3]; then
  python3 -m venv venv
else
  virtualenv venv
fi
. venv/bin/activate
pip install --upgrade pip
pip install pytest pytest-cov
pip install -e .  # install tmrg
