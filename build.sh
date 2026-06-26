#!/usr/bin/env bash
pip install -r requirements.txt
pip install gunicorn whitenoise
python manage.py migrate
python manage.py load_products products_data.csv
