#!/bin/sh

set -e
sed -Ei 's/stretch/buster/g' /etc/apt/sources.list
export DEBIAN_FRONTEND=noninteractive
apt-get update &&
  apt-get dist-upgrade -y &&
  apt-get install -y git python3-pip build-essential

git clone git@github.com:iBug/douban-spider.git /root/douban-spider
pip3 install scrapy fake-useragent requests

mkdir -p $HOME/.config/systemd/user
cp "$(dirname "$0")"/spider.service $HOME/.config/systemd/user/spider.service
systemctl --user daemon-reload
systemctl --user enable spider.service
systemctl --user start spider.service
