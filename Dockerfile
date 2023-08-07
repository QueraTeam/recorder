FROM node:latest
WORKDIR /usr/src/app
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD true
COPY ./google-chrome-stable_current_amd64.deb .
#RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt-get update &&  \
    apt-get install -y ffmpeg xvfb libasound2-dev libsndfile1-dev pulseaudio alsa-utils ./google-chrome-stable_current_amd64.deb
COPY package*.json ./
RUN npm install
RUN pulseaudio -D --exit-idle-time=-1 &&  \
    pacmd load-module module-virtual-sink sink_name=v1 &&  \
    pacmd set-default-sink v1 &&  \
    pacmd set-default-source v1.monitor
COPY . .
CMD [ "node", "recorder.js" ]
