from flask import Flask
from pymongo import MongoClient

app = Flask(__name__)

client = MongoClient("localhost", 27017)
db = client["smart_warehouse"]
collection = db["packages"]

@app.route('/')
def hello_world():
  return 'Hello, World!'

@app.route('/add_package/<int:package_id>/<str:data>')
def add_package(package_id, data):
    package = {"id": package_id, "data": data}
    collection.insert(package)
    return ''

@app.route('/orders/<int:client_id>')
def list_orders_by_client(client_id):
  return 'Hello, World!'

@app.route('/package_status/<int:package_id>')
def package_status(package_id):
  return 'Hello, World!'


if __name__ == '__main__':
    app.run(5000, debug=False)


busca = {"chave1": valor1, "chave2": {"$gt": valor2}}
ordenacao = [ ["idade", DESCENDING] ]
documento = colecao.find_one(busca, sort=ordenacao)