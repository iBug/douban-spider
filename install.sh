#!/bin/sh

set -e
sed -Ei 's/stretch/buster/g' /etc/apt/sources.list
export DEBIAN_FRONTEND=noninteractive
apt-get update &&
  apt-get dist-upgrade -y &&
  apt-get install -y git python3-pip build-essential

WORKDIR=/root/douban-spider
git clone --branch=swarm git@github.com:iBug/douban-spider.git "$WORKDIR"
pip3 install scrapy fake-useragent requests

mkdir -p $HOME/.config/systemd/user
cp "$WORKDIR"/spider.service $HOME/.config/systemd/user/spider.service
systemctl --user daemon-reload
systemctl --user enable spider.service
systemctl --user start spider.service
