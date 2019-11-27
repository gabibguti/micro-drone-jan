
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

def clear_db():
  collection.remove({})

def init_packages():
  data = {}
  for row in range(0, 2):
    data[row] = {}
    for col in range(0, 5):
      data[row][col] = False
  return data

DATA_Packages = init_packages()

@app.route('/')
def hello_world():
  print('##', DATA_Packages)
  SVG_EmptyShelf = './static/shelves.svg'
  SVG_Package = './static/box_package_color_qrcode_f.svg'
  return render_template('homepage.html',
  SVG_EmptyShelf=SVG_EmptyShelf,
  SVG_Package=SVG_Package,
  DATA_Packages=DATA_Packages)

@app.route("/refresh_shelf/", methods=['POST'])
def refresh_shelf():
    global DATA_Packages
    print("\n\n***\n")
    print("Refreshing shelf...")
    raw_data = get_all_packages()
    data = json.loads(raw_data)
    DATA_Packages = init_packages()
    for pkg in data:
      DATA_Packages[pkg["row"]][pkg["col"]] = True
    print(DATA_Packages)
    print("\n***\n\n")
    return (''), 204

@app.route('/all_packages')
def get_all_packages():
    all_packages = list(collection.find())
    for pkg in all_packages:
      pkg.pop("_id", None)
    return json.dumps(all_packages)

@app.route('/add_package/<int:package_id>/<string:date>/<int:row>/<int:col>')
def add_package(package_id, date, row, col):
    # Note: data must be in the format: YYYY-MM-DD
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
    for pkg in delayed_packages:
      pkg.pop("_id", None)
    return json.dumps(delayed_packages)

if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=False)

