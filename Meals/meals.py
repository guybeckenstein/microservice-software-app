from flask import Flask, request, jsonify
import flask
import json
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

@app.route('/dishes', methods=['POST'])
def create_dish() -> flask.Response:
    global dish_id

    data = request.get_json()
    dish_name = data[NAME]

    response = requests.get(f'https://api.calorieninjas.com/v1/nutrition?query={dish_name}', headers={
        'X-Api-Key': 'YOUR_API_KEY'  # Replace with your actual API key
    })

    if response.status_code != 200:
        return 'Failed to retrieve dish data', str(response.status_code)

    response_json = response.json()

    dish_id += 1
    calories, serving_size_g, sodium_mg, sugar_g = calculate_portions_values_sum(response_json)
    dish = {
        NAME: dish_name,
        ID: dish_id,
        CAL: calories,
        SIZE: serving_size_g,
        SODIUM: sodium_mg,
        SUGAR: sugar_g
    }
    db.dishes.insert_one(dish)  # Save the dish data in the "dishes" collection of MongoDB

    return str(dish_id), str(response.status_code)

@app.route('/dishes', methods=['GET'])
def get_dishes() -> flask.Response:
    dishes = list(db.dishes.find())  # Retrieve all dishes from the "dishes" collection
    return jsonify(dishes)

@app.route('/dishes/<dish_request>', methods=['GET'])
def get_dish(dish_request: str) -> flask.Response:
    dish = dish_request.lower()

    if dish.isdigit():
        dish_data = db.dishes.find_one({ID: int(dish)})  # Retrieve the dish from MongoDB by ID
    else:
        dish_data = db.dishes.find_one({NAME: dish})  # Retrieve the dish from MongoDB by name

    if dish_data is None:
        return 'Dish not found', str(404)

    return jsonify(dish_data), str(200)

@app.route('/dishes/<dish_request>', methods=['DELETE'])
def delete_dish(dish_request: str) -> flask.Response:
    dish = dish_request.lower()

    if dish.isdigit():
        db.dishes.delete_one({ID: int(dish)})  # Delete the dish from MongoDB by ID
    else:
        db.dishes.delete_one({NAME: dish})  # Delete the dish from MongoDB by name

    return dish, 200

@app.route('/meals', methods=['POST'])
def create_meal() -> flask.Response:
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
def get_meal(meal_request: str) -> flask.Response:
    meal = meal_request.lower()

    if meal.isdigit():
        meal_data = db.meals.find_one({ID: int(meal)})  # Retrieve the meal from MongoDB by ID
    else:
        meal_data = db.meals.find_one({NAME: meal})  # Retrieve the meal from MongoDB by name

    if meal_data is None:
        return 'Meal not found', str(404)

    return jsonify(meal_data), str(200)

@app.route('/meals/<meal_request>', methods=['DELETE'])
def delete_meal(meal_request: str) -> flask.Response:
    meal = meal_request.lower()

    if meal.isdigit():
        db.meals.delete_one({ID: int(meal)})  # Delete the meal from MongoDB by ID
    else:
        db.meals.delete_one({NAME: meal})  # Delete the meal from MongoDB by name

    return meal, str(200)

def calculate_portions_values_sum(data: dict) -> tuple:
    calories_sum = 0
    serving_size_sum = 0
    sodium_sum = 0
    sugar_sum = 0

    for item in data['items']:
        calories_sum += item['calories']
        serving_size_sum += item['serving_size_g']
        sodium_sum += item['sodium_mg']
        sugar_sum += item['sugar_g']

    return calories_sum, serving_size_sum, sodium_sum, sugar_sum

if __name__ == '__main__':
    app.run(debug=True)
