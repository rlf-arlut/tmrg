#!/bin/bash
# This scipts appends bin folder to the system search path
DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
BIN=$(cd "$DIR/../bin"; pwd)
export PATH=$BIN:$PATH
