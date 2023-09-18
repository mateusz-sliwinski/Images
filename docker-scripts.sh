#!/bin/bash

apt-get update
apt-get install -y --no-install-recommends git libpango1.0-0 libcairo2 python3-pip ssh
apt-get install -y gettext
apt-get install -y gcc
rm -rf /var/lib/apt/lists/*

