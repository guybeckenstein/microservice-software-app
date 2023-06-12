import flask
import pymongo
from flask import Flask, jsonify, request
from pymongo import MongoClient

# MongoDB configuration
client = MongoClient('mongodb://MongoDB_Container/')
db = client['ex2']  # database name
diets_collection = db['diets']

# Constant global variables
ID = '_id'                  # For dishes
NAME = 'name'               # For diets
CAL = 'cal'                 # For diets
SODIUM = 'sodium'           # For diets
SUGAR = 'sugar'             # For diets
MESSAGE = 'message'         # For responses
# Global variables
app = Flask(__name__)       # For running flask (requests & responses)


def name_to_id_generator(instance_to_add_name: str, collection: pymongo.cursor.Cursor) -> bool:
    """
    :param instance_to_add_name: Name of instance we want to add, checking if it is already in the collection
    :param collection: All instances of a collection in MongoDB, we will iterate over it
    :return: Integer value of a dish or meal ID - positive if found, -1 if not
    """
    for instance in collection:
        if instance[NAME] == instance_to_add_name:
            return False
    return True


@app.route('/diets', methods=['POST'])
def create_diet() -> flask.Response:
    global diets_collection
    if request.content_type != 'application/json':
        return jsonify("POST expects content type to be application/json"), str(415)
    else:
        diet_name = request.json.get(NAME, None)
        if diet_name is None:
            return str(-1), str(400)
        elif name_to_id_generator(diet_name, diets_collection.find()) is False:
            return jsonify(f'Diet with {diet_name} already exists'), str(422)

        calories = request.json.get(CAL, None)
        sodium = request.json.get(SODIUM, None)
        sugar = request.json.get(SUGAR, None)

        if (calories is None) or (sodium is None) or (sugar is None):
            return jsonify('Incorrect POST format'), str(422)
        else:
            diet = {
                NAME: diet_name,
                CAL: calories,
                SODIUM: sodium,
                SUGAR: sugar
            }
            diets_collection.insert_one(diet)
            return jsonify(f'Diet {diet_name} was created successfully'), str(201)


@app.route('/diets', methods=['GET'])
def get_diets() -> flask.Response:
    global diets_collection
    diets = [diet for diet in list(diets_collection.find())]
    # Convert ObjectId (`_id`) values to strings
    for diet in diets:
        diet['_id'] = str(diet['_id'])
    return jsonify(diets), str(200)


@app.route('/diets/<diet_name>', methods=['GET'])
def get_diet_by_name(diet_name: str) -> tuple[flask.Response, str]:
    global diets_collection
    if (diet_name is None) or (diet_name == ""):
        return str(-1), str(400)
    diet = list(diets_collection.find({NAME: diet_name}))
    if len(diet) == 0:
        return jsonify(f'Diet {diet_name} not found'), str(404)
    else:
        res_diet = diet[0]
        res_diet['_id'] = str(res_diet['_id'])
        return jsonify(res_diet), str(200)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5002)
