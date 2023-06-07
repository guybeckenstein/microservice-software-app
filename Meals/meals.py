from flask import Flask, request, jsonify
import flask
import requests
from pymongo import MongoClient

app = Flask(__name__)

# MongoDB configuration
client = MongoClient("mongodb://localhost:27017/")
db = client["mydatabase"]  # Replace "mydatabase" with the name of your database

# Constants
ID = "id"
NAME = "name"
CAL = "calories"
SIZE = "serving_size_g"
SODIUM = "sodium_mg"
SUGAR = "sugar_g"
APPETIZER = "appetizer"
MAIN = "main"
DESSERT = "dessert"

dish_id = 0
meal_id = 0

API_KEY = 'MktCMe6vJqb/xCbZ10IBgA==5utKBDSANyr1ZXUN'


@app.route('/dishes', methods=['POST'])
def create_dish() -> tuple[str, str]:
    global dish_id
    global API_KEY

    data = request.get_json()
    if NAME not in data:
        return str(-1), str(400)
    dish_name = data[NAME]

    api_url = f'http://api.api-ninjas.com/v1/nutrition?query={dish_name}'
    response: requests.models.Response = requests.get(api_url, headers={'X-Api-Key': API_KEY})

    if response.status_code != 200:
        return 'Failed to retrieve dish data', str(response.status_code)

    response_json = response.json()[0]

    dish_id += 1
    dish = {
        NAME: dish_name,
        ID: dish_id,
        CAL: response_json['calories'],
        SIZE: response_json['serving_size_g'],
        SODIUM: response_json['sodium_mg'],
        SUGAR: response_json['sugar_g'],
    }
    db.dishes.insert_one(dish)  # Save the dish data in the "dishes" collection of MongoDB

    return str(dish_id), str(response.status_code)


@app.route('/dishes', methods=['GET'])
def get_dishes() -> flask.Response:
    dishes = list(db.dishes.find())  # Retrieve all dishes from the "dishes" collection
    return jsonify(dishes)


@app.route('/dishes/<dish_request>', methods=['GET'])
def get_dish(dish_request: str) -> tuple:
    dish = dish_request.lower()

    if dish.isdigit():
        dish_data = db.dishes.find_one({ID: int(dish)})  # Retrieve the dish from MongoDB by ID
    else:
        dish_data = db.dishes.find_one({NAME: dish})  # Retrieve the dish from MongoDB by name

    if dish_data is None:
        return 'Dish not found', str(404)

    return jsonify(dish_data), str(200)


@app.route('/dishes/<dish_request>', methods=['DELETE'])
def delete_dish(dish_request: str) -> tuple[str, str]:
    dish = dish_request.lower()

    if dish.isdigit():
        db.dishes.delete_one({ID: int(dish)})  # Delete the dish from MongoDB by ID
    else:
        db.dishes.delete_one({NAME: dish})  # Delete the dish from MongoDB by name

    return dish, str(200)


@app.route('/meals', methods=['POST'])
def create_meal() -> tuple[str, str]:
    global meal_id

    data = request.get_json()
    meal_name = data[NAME]
    appetizer_id = data[APPETIZER]
    main_id = data[MAIN]
    dessert_id = data[DESSERT]

    # Fetch dish data from MongoDB
    appetizer_data = db.dishes.find_one({ID: appetizer_id})
    main_data = db.dishes.find_one({ID: main_id})
    dessert_data = db.dishes.find_one({ID: dessert_id})

    if appetizer_data is None or main_data is None or dessert_data is None:
        return 'Invalid dish IDs', str(404)

    meal_id += 1
    meal = {
        NAME: meal_name,
        ID: meal_id,
        APPETIZER: appetizer_data,
        MAIN: main_data,
        DESSERT: dessert_data
    }
    db.meals.insert_one(meal)  # Save the meal data in the "meals" collection of MongoDB

    return str(meal_id), str(200)


@app.route('/meals', methods=['GET'])
def get_meals() -> flask.Response:
    meals = list(db.meals.find())  # Retrieve all meals from the "meals" collection
    return jsonify(meals)


@app.route('/meals/<meal_request>', methods=['GET'])
def get_meal(meal_request: str) -> tuple:
    meal = meal_request.lower()

    if meal.isdigit():
        meal_data = db.meals.find_one({ID: int(meal)})  # Retrieve the meal from MongoDB by ID
    else:
        meal_data = db.meals.find_one({NAME: meal})  # Retrieve the meal from MongoDB by name

    if meal_data is None:
        return 'Meal not found', str(404)

    return jsonify(meal_data), str(200)


@app.route('/meals/<meal_request>', methods=['DELETE'])
def delete_meal(meal_request: str) -> tuple:
    meal = meal_request.lower()

    if meal.isdigit():
        db.meals.delete_one({ID: int(meal)})  # Delete the meal from MongoDB by ID
    else:
        db.meals.delete_one({NAME: meal})  # Delete the meal from MongoDB by name

    return meal, str(200)


@app.route('/meals/<meal_request>', methods=['PUT'])
def update_meal(meal_request: str):
    """
    PUT request of /meals endpoint. Returns a meal with the given ID or name
    :param meal_request: Query param for PUT request of /meals endpoint. It is an ID of a given meal.
    :return: JSON of the meal for valid request, (-1, 400) if the query parameter is empty, (-5, 404) if the ID or name
    don't exist
    """
    if (meal_request is None) or (meal_request == ""):
        # If neither the meal ID nor a meal name is specified, the PUT request returns the response -1 with
        # error code 400 (Bad Request).
        return str(-1), str(400)

    meal_id = int(meal_request)
    meal_data = db.meals.find_one({ID: meal_id})  # Retrieve the meal from MongoDB by ID

    if meal_data is None:
        return 'Meal not found', str(404)

    # Get new meal values from JSON
    meal_name = request.json.get(NAME, None)
    appetizer_id = request.json.get(APPETIZER, None)
    main_id = request.json.get(MAIN, None)
    dessert_id = request.json.get(DESSERT, None)

    # Bad request: one of the required parameters was not specified correctly
    if (meal_name is None) or (appetizer_id is None) or (main_id is None) or (dessert_id is None):
        return str(-1), str(400)

    # Validate dishes
    appetizer_data = db.dishes.find_one({ID: appetizer_id})
    main_data = db.dishes.find_one({ID: main_id})
    dessert_data = db.dishes.find_one({ID: dessert_id})

    if (appetizer_data is None) or (main_data is None) or (dessert_data is None):
        return 'Invalid dish IDs', str(404)

    # Update meal data
    meal_data[NAME] = meal_name
    meal_data[APPETIZER] = appetizer_data
    meal_data[MAIN] = main_data
    meal_data[DESSERT] = dessert_data

    # Update the meal in MongoDB
    db.meals.update_one({ID: meal_id}, {"$set": meal_data})

    return jsonify(meal_data), str(200)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5001)
