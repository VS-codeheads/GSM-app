from flask import Flask, jsonify, request
import products_dao
import uom_dao
import json
import order_dao
from sql_connection import get_sql_connection

app = Flask(__name__)

connection = get_sql_connection()

@app.route('/getProducts', methods=['GET'])

def get_products():
    products = products_dao.get_all_products(connection)
    response = jsonify(products)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/getUOM', methods=['GET'])

def get_uom():
    response = uom_dao.get_all_uoms(connection)
    response = jsonify(response)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/addProduct', methods=['POST'])
def add_product():
    request_data = request.form['data']
    new_product_id = products_dao.insert_new_product(connection, request_data)
    response = jsonify({
        "product_id": new_product_id
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response 


@app.route('/deleteProduct/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    return_id = products_dao.delete_product(connection, request.form['product_id'])
    response = jsonify({
        "product_id": return_id
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

if __name__ == '__main__':
    print("Starting Flask server for GSM system")
    app.run(port=5000)   


@app.route('/addOrder', methods=['POST'])
def add_order():
    request_data = json.loads(request.form['data'])
    new_order_id = order_dao.add_order(connection, request_data)
    response = jsonify({
        "order_id": new_order_id
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

