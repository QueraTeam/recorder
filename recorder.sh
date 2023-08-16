#!/bin/bash

RECORD_TIMEOUT=${1}
FILE_NAME=${2}
USERNAME=${3}
PASSWORD=${4}
RECORD_URL=${5}
VOD_API_KEY=${6}
VOD_BASE_URL=${7}
VOD_CHANNEL_KEY=${8}
CALLBACK_URL=${9}


pulseaudio -D --exit-idle-time=-1
pacmd load-module module-virtual-sink sink_name=v1
pacmd set-default-sink v1
pacmd set-default-source v1.monitor
mkdir -p /output/video/
timeout ${RECORD_TIMEOUT} node recorder.js ${FILE_NAME} ${USERNAME} ${PASSWORD} ${RECORD_URL}
python3 uploader.py "${VOD_API_KEY}" ${VOD_BASE_URL} ${VOD_CHANNEL_KEY} /output/video/${FILE_NAME}.mp4 ${CALLBACK_URL}
