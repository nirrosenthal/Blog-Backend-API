FROM ubuntu:20.04

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && apt-get clean

WORKDIR /app
RUN mkdir -p /app

COPY ./src ./src/
COPY ./requirements.txt .

RUN pip3 install --no-cache-dir -r requirements.txt

