#!/bin/sh
flask db upgrade  # применяем миграции
exec gunicorn -b 0.0.0.0:5000 main:app