from flask import Flask
from flask_pymongo import PyMongo
from config import MONGO_URI,SECRET_KEY

app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY
app.config["MONGO_URI"] = MONGO_URI

# "mongodb+srv://Respect:<respect001>@cluster0.fclyhzv.mongodb.net/?retryWrites=true&w=majority"

mongodb_client = PyMongo(app)
db = mongodb_client.db
from routers import *


if __name__ == "__main__":
    app.run(debug=True)