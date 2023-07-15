#!/bin/bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/cnfc
python3 -m unittest discover
