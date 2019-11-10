#!/bin/bash
set -e

echo "Installing dependencies"
/usr/bin/python3 -m pip install -r requirements.txt

echo "Installing the Acme-Client script and service"
cp acmebot-client.py /usr/bin/acmebot-client.py
cp acmebot-client.service /lib/systemd/system/acmebot-client.service

echo "Enable the Acme-Client Service"

systemctl daemon-reload 
systemctl enable acmebot-client.service
systemctl start acmebot-client.service
systemctl status acmebot-client.service