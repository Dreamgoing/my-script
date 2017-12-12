#!/bin/bash -e
find . -not \( -path './env' -prune \) -name '*.pyc' -exec rm -f {} \;

