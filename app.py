
from flask import Flask, render_template, jsonify
from pymongo import MongoClient
from datetime import datetime
import json

app = Flask(__name__, template_folder='template', static_folder='static')

client = MongoClient("localhost", 27017)
db = client["smart_warehouse"]
collection = db["packages"]

# TODO add more status about the package
# package:
# {
#     "id": <int>
#     "date": <str: YYYY-MM-DD>
#     "status": ["delayed", "ok"]
# }

def update_all():
    # Update and get all packages
    packages = list(collection.find())
    for package in packages:
        new_status = check_status(package["date"])
        if new_status != package["status"]:
            package["status"] = new_status
            # TODO use pymongo $set to update values, instead of adding new ones
            # db.update({"_id": package_id}, {"$set": package })
            collection.insert(package)

def check_status(dt):
    date = datetime.strptime(dt, "%Y-%m-%d")
    return "okay" if date > datetime.now() else "delayed"

@app.route('/')
def hello_world():
  SVG_EmptyShelf = './static/shelves.svg'
  SVG_Package = './static/box_package_color_qrcode_f.svg'
  return render_template('homepage.html', SVG_EmptyShelf=SVG_EmptyShelf, SVG_Package=SVG_Package)

@app.route('/add_package/<int:package_id>/<string:date>')
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
    query = {"id": package_id}
    package = collection.find_one(query)
    package.pop("_id", None)
    # update package status
    new_status = check_status(package["date"])
    if new_status != package["status"]:
        package["status"] = new_status
        # TODO use pymongo $set to update values, instead of adding new ones
        # db.update({"_id": package_id}, {"$set": package })
        collection.insert(package)
    print(json.dumps(package))
    return json.dumps(package)
    # return json.dumps(package)

@app.route('/delayed_package')
def get_delayed_package():
    update_all()
    delayed_packages = list(collection.find({"status": "delayed"}))
    return json.dumps(delayed_packages)

if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=False)
