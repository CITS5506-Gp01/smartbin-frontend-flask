#!/bin/bash
# run the app locally
python3 -m venv venv &&
source venv/bin/activate &&
pip3 install -r requirements.txt &&
flask run