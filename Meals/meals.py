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


if __name__ == '__main__':
    app.run(debug=True)
