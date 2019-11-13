from flask import Flask
from pymongo import MongoClient
from datetime import datetime
import json

app = Flask(__name__)

client = MongoClient("localhost", 27017)
db = client["smart_warehouse"]
collection = db["packages"]

def update_all():
    # Update and get all packages
    packages = list(collection.find())
    for package in packages:
        new_status = check_status(package["date"])
        if new_status != package["status"]:
            package["status"] = new_status
            # TODO use pymongo $set to update values, instead of adding new ones
            # db.update({"id": package_id}, {"$set": package })
            collection.insert(package)

def check_status(dt):
    return "okay" if dt > datetime.now() else "delayed"

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/add_package/<int:package_id>/<str:date>')
def add_package(package_id, date):
    # Note: data must be in the format: YYYY-MM-DD
    dt = date.split('-')
    year = int(dt[0])
    month = int(dt[1])
    day = int(dt[2])
    now = datetime.now()
    arrival = datetime(year, month, day)
    status = "okay" if arrival > now else "delayed"
    package = {"id": package_id, "date": date, "status": status}
    collection.insert(package)
    return 'Package info added to database'

@app.route('/package_status/<int:package_id>')
def package_status(package_id):
    search = {"id": package_id}
    package = collection.find_one(search)

    # update package status
    new_status = check_status(package["date"])
    if new_status != package["status"]:
        package["status"] = new_status
        # TODO use pymongo $set to update values, instead of adding new ones
        # db.update({"id": package_id}, {"$set": package })
        collection.insert(package)
    return json.dumps(package)

@app.route('/delayed_package')
def get_delayed_package():
    update_all()
    delayed_packages = list(collection.find({"status": "delayed"}))
    return json.dumps(delayed_packages)

if __name__ == '__main__':
    app.run(5000, debug=False)


