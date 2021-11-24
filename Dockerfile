FROM python:3.10.0-slim-buster

ENV PIP_NO_CACHE_DIR 1 

RUN sed -i.bak 's/us-west-2\.ec2\.//' /etc/apt/sources.list

RUN apt-get update && apt-get upgrade -y

RUN apt-get install -y ffmpeg python3-pip curl
RUN pip3 install --upgrade pip setuptools

ENV PATH="/home/bot/bin:$PATH"

RUN mkdir /Natsunagi/
COPY . /Natsunagi 
WORKDIR /Natsunagi

RUN pip3 install -U -r requirements.txt

CMD ["python3", "-m", "Natsunagi"]
