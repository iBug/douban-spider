#!/bin/sh

exec docker build -t spiderserver:latest "$(dirname "$0")"
