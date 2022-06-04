#!/bin/sh

if [ -n "$CERT_FILE" ] && [ -n "$KEY_FILE" ]
then
    # TODO implement https health check
    echo "https health check not supported yet :("
else
    args="http://127.0.0.1:$PORT/is-healthy"
    python -m web_health_checker $args
fi
