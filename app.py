from flask import Flask
from flask import render_template

app = Flask(__name__)

#from app import routes

@app.route('/')
def index():    
    return render_template('index.html')
