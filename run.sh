#!/bin/sh

if [ -z "$USER_AGENT" ]; then
  USER_AGENT='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'
fi

exec scrapy runspider spider.py -o result.json -s USER_AGENT="$USER_AGENT"
