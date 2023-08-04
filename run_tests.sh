#!/bin/bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/cnfc:$(pwd)/tests
PATTERN=${1:-'*'}
python3 -m unittest discover -k "$PATTERN"
