
from flask import Flask, render_template, jsonify, redirect, url_for
from pymongo import MongoClient
from datetime import datetime
import json
from time import sleep

# Interface settings
app = Flask(__name__, template_folder='template', static_folder='static')

# Database settings
client = MongoClient("localhost", 27017)
db = client["smart_warehouse"]
collection = db["packages"]

# Interface Functions/Routes

def init_packages():
  data = {}
  for row in range(0, 2):
    data[row] = {}
    for col in range(0, 5):
      data[row][col] = None
  return data

def init_shelf():
  return {
      "total": 10,
      "busy": 0,
      "free": 10
    }

DATA_Shelf = init_shelf()
DATA_Packages = init_packages()
CURR_Package = None
SVG_EmptyShelf = './static/shelves.svg'
SVG_Package = './static/box_package_color_qrcode_f.svg'

@app.route('/')
def hello_world():
  global DATA_Packages
  return render_template('homepage.html',
  SVG_EmptyShelf=SVG_EmptyShelf,
  SVG_Package=SVG_Package,
  DATA_Packages=DATA_Packages,
  CURR_Package=CURR_Package,
  DATA_Shelf=DATA_Shelf)

@app.route("/refresh_shelf/", methods=['POST'])
def refresh_shelf():
    global DATA_Packages, DATA_Shelf
    sleep(5)
    # Fetch packages
    raw_data = get_all_packages()
    data = json.loads(raw_data)
    # Set new packages data
    DATA_Packages = init_packages()
    for pkg in data:
      DATA_Packages[pkg["row"]][pkg["col"]] = pkg["id"]
    DATA_Shelf = {
      "total": 10,
      "busy": len(data),
      "free": 10 - len(data)
    }
    # Reload page
    return redirect(url_for('hello_world'))

@app.route("/package_details/<int:id>")
def get_package_details(id):
  global CURR_Package
  raw_data = get_package(id)
  data = json.loads(raw_data)

  CURR_Package=data
  # Reload page
  return redirect(url_for('hello_world'))


# Server Functions/Routes
# TODO add more status about the package 
# package:
# {
#     "id": <int>
#     "date": <str: YYYY-MM-DD>
#     "status": ["delayed", "ok"]
#     "row": <int>
#     "col": <int>
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

@app.route('/all_packages')
def get_all_packages():
    all_packages = list(collection.find())
    for pkg in all_packages:
      pkg.pop("_id", None)
    return json.dumps(all_packages)

@app.route('/add_package/<int:package_id>/<string:date>/<int:row>/<int:col>')
def add_package(package_id, date, row, col):
    # Note: data must be in the format: YYYY-MM-DD

    package = list(collection.find({"id": package_id}))
    if(len(package) != 0):
      return "Package already exists"
    package = list(collection.find({"row": row, "col": col}))
    if(len(package) != 0 or row not in range(0, 2) or col not in range(0, 5)):
      return "Space not avaiable in shelf"

    dt = date.split('-')
    year = int(dt[0])
    month = int(dt[1])
    day = int(dt[2])
    now = datetime.now()
    arrival = datetime(year, month, day)
    status = "okay" if arrival > now else "delayed"
    package = {
      "id": package_id,
      "date": date,
      "status": status,
      "row": row,
      "col": col
    }
    collection.insert(package)
    return 'Package info added to database'

@app.route('/package/<int:package_id>')
def get_package(package_id):
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
    for pkg in delayed_packages:
      pkg.pop("_id", None)
    return json.dumps(delayed_packages)

@app.route('/clear_data')
def clear_database():
    collection.remove({})
    return 'Base de dados resetada!'

# Run App
if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)

