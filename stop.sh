#!/bin/bash

cd "$(dirname -- "${BASH_SOURCE[0]}")" || exit

# remove the flag file indicating we don't want streaming to continue
rm -f streaming_flag.txt

# end the encoder if it's running
killall --user "$USER" --ignore-case --signal INT ffmpeg

# set up the python env and run script to close the streaming container
source .venv/bin/activate

python3 stream_ender.py > /dev/null 2> py_error.log

deactivate

