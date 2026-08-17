#!/bin/bash

# set up python environmnet, run script to create stream container
cd "$(dirname -- "${BASH_SOURCE[0]}")" || exit

source .venv/bin/activate

python3 stream_starter.py > /dev/null 2> py_error.log

deactivate

# create a flag file indicating we want streaming to continue
touch streaming_flag.txt

# start the encoder monitor - this can take the place of starting the encoder
./stream_tender.sh > stream_tender.log &
