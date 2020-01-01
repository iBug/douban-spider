#!/bin/bash

is_number() {
  case "$1" in
    ''|*[!0-9]*) return 1;;
    *) return 0;;
  esac
}

get_records() {
  sqlite3 /root/douban-spider/spider.db 'SELECT COUNT(*) FROM records;'
}

get_urls() {
  sqlite3 /root/douban-spider/spider.db 'SELECT COUNT(*) FROM urls;'
}

get_time() {
  date +%s
}

if [ ! -e last_count ]; then
  FAIL=1
elif [ ! -e last_time ]; then
  FAIL=1
fi

if [ -n "$FAIL" ]; then
  echo "No previous record found"
  get_records > last_count
  get_time > last_time
else
  LAST_COUNT="$(<last_count)"
  LAST_TIME="$(<last_time)"
  get_records > last_count
  get_time > last_time
  THIS_COUNT="$(<last_count)"
  THIS_TIME="$(<last_time)"
  if is_number "$THIS_COUNT" && is_number "$THIS_TIME"; then
    python3 -c "print('$THIS_COUNT',($THIS_COUNT-$LAST_COUNT)/($THIS_TIME-$LAST_TIME))"
  else
    # Bad new value, restore old
    echo "$LAST_COUNT" > last_count
    echo "$LAST_TIME" > last_time
  fi
fi

if [ "$#" -ne 0 ]; then
  get_urls
fi
