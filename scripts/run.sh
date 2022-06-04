#!/bin/sh

BIND="$HOST:$PORT"
args="--bind $BIND --workers $WORKERS --log-level $LOG_LEVEL"

if [ -n "$CERT_FILE" ] && [ -n "$KEY_FILE" ]
then
    args="$args --certfile $CERT_FILE --keyfile $KEY_FILE"
    # TODO remove warning when https health check is implemented
    echo "https health check not supported yet :("
fi

hypercorn 'web_portal.main:create_app()' $args
