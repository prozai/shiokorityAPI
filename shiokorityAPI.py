from flask import Flask, jsonify, render_template
from flask_cors import CORS
from config import config
import os

#This is Root route for this application, so if needed just create a blueprint for your controller, do not create your own app route in your controller.
app = Flask(__name__,template_folder=r"app\\templates")

CORS(app)
config_name = os.getenv('FLASK_ENV', 'testing')
app.config.from_object(config[config_name])

#here is the blueprint 
from app.controller.merchantController import merchantBlueprint
app.register_blueprint(merchantBlueprint)

from app.controller.administratorController import adminBlueprint
app.register_blueprint(adminBlueprint)

@app.route("/")
def hello():
    return "this is main page without anything"

if __name__ == "__main__":
    app.run()
    
