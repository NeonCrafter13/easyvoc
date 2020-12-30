#!/bin/bash
cd /var/www/Server
gunicorn -b 0.0.0.0:5000 main:app -w 5