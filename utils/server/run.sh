#!/bin/sh

docker rm -f spiderserver
docker run -d --name=spiderserver \
  -v /root/douban-spider/spider.db:/spider.db:rw \
  -p 5001:5001 \
  spiderserver:latest
