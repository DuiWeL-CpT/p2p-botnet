#!/bin/bash

# Activate conda environment
conda env update -f environment.yml
conda activate demo_botnet_p2p

# Execute tests
pytest ./python/tests/unit_tests/
