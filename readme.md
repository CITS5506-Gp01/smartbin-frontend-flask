
# Flask webapp for smartbin monitoring system

# Getting started
## Set up and enter the python virtual envrionment

python3 -m venv venv 
source venv/bin/activate 

# update and install dependencies (make sure to upgrade pip)
pip3 install --upgrade pip
pip3 install -r requirements.txt 

# run the app
# requires an environment variable file ".env" in the same directory containing all the required variables

flask run
