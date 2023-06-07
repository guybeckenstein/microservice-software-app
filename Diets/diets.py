from flask import Flask, jsonify, request, Response
from pymongo import MongoClient

# MongoDB configuration
client = MongoClient("mongodb://localhost:27017/")
db = client["mydatabase"]  # Replace "mydatabase" with the name of your database
collection = db["diets"]   # Replace "diets" with the name of your collection

# Constant global Variables
NAME = 'name'               # For diets
MESSAGE = 'message'         # For responses

# Global variables
app = Flask(__name__)


@app.route('/diets', methods=['POST'])
def create_diet() -> tuple:
    new_diet = request.get_json()
    diet_name = new_diet[NAME]

    # Check if diet with the same name already exists
    existing_diet = collection.find_one({NAME: diet_name})
    if existing_diet:
        return jsonify({MESSAGE: 'Diet with the same name already exists'}), 400

    # Insert the new diet into the collection
    collection.insert_one(new_diet)

    return jsonify({MESSAGE: 'Diet created successfully'}), 201


@app.route('/diets', methods=['GET'])
def get_diets() -> Response:
    diets = list(collection.find())
    return jsonify(diets)


@app.route('/diets/<name>', methods=['GET'])
def get_diet_by_name(name: str) -> tuple[Response, str]:
    diet = collection.find_one({NAME: name})
    if diet:
        return jsonify(diet), str(200)
    return jsonify({MESSAGE: 'Diet not found'}), str(404)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5002)
