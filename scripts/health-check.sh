#!/bin/sh

if [ -n "$CERT_FILE" ] && [ -n "$KEY_FILE" ]
then
    args="https://127.0.0.1:$PORT/is-healthy --allow-unverified"
else
    args="http://127.0.0.1:$PORT/is-healthy"
fi

python -m web_health_checker $args
