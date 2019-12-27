#!/bin/sh

cd "$(dirname "$0")"
python3 spider.py

if [ -n "$FLOCK_MODE" -a -e "should_reboot" -a "$(id -u)" -eq 0 ]; then
  reboot
fi
