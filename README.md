# Screen Recorder
to build the docker file run this:
```
docker build -t recorder .
```

to run the container:
```
docker run -v /home/test/Videos/:/output/video/ recorder timeout username password url
```