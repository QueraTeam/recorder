FROM node:latest
WORKDIR /usr/src/app
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD true
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt-get update && \
    apt-get install -y ffmpeg xvfb libasound2-dev libsndfile1-dev pulseaudio alsa-utils python3-pip python3-venv ./google-chrome-stable_current_amd64.deb && \
    rm -rf /var/lib/apt/lists/* ./google-chrome-stable_current_amd64.deb
COPY package*.json ./
RUN npm ci && python3 -m pip install requests==2.31.0
COPY . .
ENTRYPOINT ["/bin/bash", "recorder.sh"]
