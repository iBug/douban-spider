#!/bin/sh

export DEBIAN_FRONTEND=noninteractive
apt-get update &&
  apt-get upgrade &&
  apt-get install -y git python3-pip build-essential

pip3 install scrapy fake-useragent requests

mkdir -p $HOME/.config/systemd/user
cp "$(dirname "$0")"/spider.service $HOME/.config/systemd/user/spider.service
systemctl --user daemon-reload
systemctl --user enable spider.service
systemctl --user start spider.service
