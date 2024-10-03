#!/bin/sh
mkdir -p /run/nginx

cat /etc/resolv.conf |
    sed -rn 's/^nameserver\s+([0-9.]+)\s*$/resolver \1;/p' \
        > /run/nginx/resolver.conf
