#!/bin/bash

RECORD_TIMEOUT=${1}
USERNAME=${2}
PASSWORD=${3}
RECORD_URL=${4}

pulseaudio -D --exit-idle-time=-1
pacmd load-module module-virtual-sink sink_name=v1
pacmd set-default-sink v1
pacmd set-default-source v1.monitor
timeout ${RECORD_TIMEOUT} node recorder.js ${USERNAME} ${PASSWORD} ${RECORD_URL}
# ffmpeg -i input.mkv -codec copy output.mp4
# rm input.mkv