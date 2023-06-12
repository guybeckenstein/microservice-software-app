import pymongo
from flask import Flask, request, jsonify
import flask
import json
import requests
from pymongo import MongoClient

# MongoDB configuration
client = MongoClient('mongodb://MongoDB_Container/')
db = client['ex2']  # database name
dishes_collection = db['dishes']
meals_collection = db['meals']

# Constant global variables
NAME = 'name'               # For dishes
ID = 'ID'                   # For dishes
SIZE = 'size'               # For dishes
CAL = 'cal'                 # For dishes
SODIUM = 'sodium'           # For dishes
SUGAR = 'sugar'             # For dishes
APPETIZER = 'appetizer'     # For meals
MAIN = 'main'               # For meals
DESSERT = 'dessert'         # For meals
# Global variables
app = Flask(__name__)       # For running flask (requests & responses)
API_KEY = 'MktCMe6vJqb/xCbZ10IBgA==5utKBDSANyr1ZXUN'
# Global calculations
dish_id = 0
for dish in dishes_collection.find():
    if dish_id < int(dish[ID]):
        dish_id = int(dish[ID])
meal_id = 0
for meal in meals_collection.find():
    if meal_id < int(meal[ID]):
        meal_id = int(meal[ID])


# Dishes
@app.route('/dishes', methods=['POST'])
def create_dish() -> flask.Response:
    """
    POST request of /dishes endpoint. Adds a dish with the given name in the JSONic body
    :return: ID of the new dish, if there are no edge cases
    """
    global dish_id
    if request.content_type != 'application/json':
        return str(0), str(415)

    dish_name = request.json.get(NAME, None)
    if dish_name is None:
        return str(-1), str(400)
    response_json: dict = get_dish_nutrition_info(dish_name)
    if response_json == {False}:
        return str(-3), str(400)
    if response_json == {True}:
        return str(-4), str(400)
    response_id, response_code = validate_dish_json_parameters(dish_name, response_json)
    if response_id is not None:
        return str(response_id), str(response_code)
    else:
        # Creates a new dish and adds it to our RESTful API
        dish_id += 1
        dish = {
            ID: str(dish_id),
            NAME: dish_name,
            CAL: response_json['calories'],
            SIZE: response_json['serving_size_g'],
            SODIUM: response_json['sodium_mg'],
            SUGAR: response_json['sugar_g']
        }
        dishes_collection.insert_one(dish)
        return str(dish_id), str(response_code)


def validate_dish_json_parameters(dish_name: str, response_json: dict) -> tuple:
    """
    :param dish_name: Name of the dish we are adding, given in the original request
    :param response_json: Response list of the original request (including query parameter NAME), given by Ninjas API
    :return: (None, 201) if the request is valid, (-2, 400) if the dish already exists, (-3, 400) if the dish does not
    exist in Ninjas API
    """
    global dishes_collection
    if name_to_id_generator(dish_name, dishes_collection.find()) != -1:
        return -2, 400
    elif response_json is None:
        return -3, 400
    return None, 201


def name_to_id_generator(instance_to_add_name: str, collection: pymongo.cursor.Cursor) -> int:
    """
    :param instance_to_add_name: Name of instance we want to add, checking if it is already in the collection
    :param collection: All instances of a collection in MongoDB, we will iterate over it
    :return: Integer value of a dish or meal ID - positive if found, -1 if not
    """
    for instance in collection:
        if instance[NAME] == instance_to_add_name:
            return int(instance[ID])
    return -1


def get_dish_nutrition_info(dish_name: str) -> dict:
    """
    :param dish_name: Name of the dish we are adding, given in the original request.
    :return: Response for the original request (including query parameter NAME), given by Ninjas API.
    """
    api_url = f'http://api.api-ninjas.com/v1/nutrition?query={dish_name}'
    response: requests.models.Response = requests.get(api_url, headers={'X-Api-Key': API_KEY})
    if response.status_code != 200:
        return {True}
    data: list = response.json()
    if len(data) == 0:
        return {False}
    return data[0]


@app.route('/dishes', methods=['GET'])
def get_dishes() -> flask.Response:
    """
    GET request of /dishes endpoint
    :return: JSON file of all dishes
    """
    global dishes_collection
    dishes = [dish for dish in list(dishes_collection.find())]
    # Convert ObjectId (`_id`) values to strings
    for dish in dishes:
        dish['_id'] = str(dish['_id'])
    return jsonify(dishes)


@app.route('/dishes/<dish_request>', methods=['GET'])
def get_dish(dish_request: str) -> flask.Response:
    """
    GET request of /dishes endpoint. Returns a dish with the given ID or name
    :param dish_request: Query parameter for GET request of /dishes endpoint. It may be an ID or a name of a given dish.
    :return: JSON of the dish for valid request, (-1, 400) if the query parameter is empty, (-5, 404) if the ID or name
    don't exist
    """
    global dishes_collection, dish_id
    if (dish_request is None) or (dish_request == ""):
        return str(-1), str(400)
    elif dish_request.isdigit() is True:
        dish = int(dish_request)
        if validate_instance_id(dish, dishes_collection) is False:
            return str(-5), str(404)
    else:
        dish_name = dish_request
        dish = name_to_id_generator(dish_name, dishes_collection.find())
        if dish == -1:
            return str(-5), str(404)

    res_dish = list(dishes_collection.find({ID: str(dish)}))[0]
    res_dish['_id'] = str(res_dish['_id'])
    return jsonify(res_dish), str(200)


def validate_instance_id(instance_id, collection):
    """
    :param instance_id: An ID of a dish, given by a client
    :param collection: Some collection from MongoDB
    :return: Integer value of a dish or meal ID - positive if found, -1 if not
    """
    for dish in collection.find():
        if dish[ID] == str(instance_id):
            return True
    return False


@app.route('/dishes/<dish_request>', methods=['DELETE'])
def delete_dish(dish_request: str) -> flask.Response:
    """
    DELETE request of /dishes endpoint. Deletes a dish with the given ID or name
    :param dish_request: Query param for DELETE request of /dishes endpoint
    :return: ID of the dish for valid request, (-1, 400) if the query parameter is empty, (-5, 404) if the ID or name
    don't exist
    """
    global dishes_collection, dish_id, meals_collection
    if (dish_request is None) or (dish_request == ""):
        return str(-1), str(400)
    elif dish_request.isdigit() is True:
        dish = int(dish_request)
        if validate_instance_id(dish, dishes_collection) is False:
            return str(-5), str(404)
    else:
        dish_name = dish_request
        dish = name_to_id_generator(dish_name, dishes_collection.find())
        if dish == -1:
            return str(-5), str(404)

    # Set the dish to null in all meals if it is part of a meal
    query = {ID: str(dish)}
    dish_instance = dishes_collection.find(query)
    for meal in meals_collection.find():
        is_dish_in_meal = False
        if meal[APPETIZER] == dish:
            meal[APPETIZER] = None
            is_dish_in_meal = True
        elif meal[MAIN] == dish:
            meal[MAIN] = None
            is_dish_in_meal = True
        elif meal[DESSERT] == dish:
            meal[DESSERT] = None
            is_dish_in_meal = True
        # Update meal values
        if is_dish_in_meal is True:
            update_query = {
                '$set': {
                    CAL: meal[CAL] - dish_instance[CAL],
                    SODIUM: meal[SODIUM] - dish_instance[SODIUM],
                    SUGAR: meal[SUGAR] - dish_instance[SUGAR],
                }
            }
            meals_collection.update_one({ID: meal[ID]}, update_query)
    # Remove dish from dishes
    dishes_collection.find_one_and_delete(query)

    return str(dish), str(200)


# Meals
@app.route('/meals', methods=['POST'])
def create_meal() -> flask.Response:
    """
    A meal object is different from a dish object. While it also has the "cal", "sodium" and "sugar" fields,
    it does not have the serving "size" field.
    POST request of /meals endpoint. Adds a meal with the given name and dishes in the JSONic body
    :return: an ID of our new meal, if there are no edge-cases
    """
    global dishes_collection, meals_collection, meal_id
    if request.content_type != 'application/json':
        return str(0), str(415)

    # Get new meal values from JSON
    meal_name = request.json.get(NAME, None)
    appetizer_id = request.json.get(APPETIZER, None)
    main_id = request.json.get(MAIN, None)
    dessert_id = request.json.get(DESSERT, None)
    if (meal_name is None) or (appetizer_id is None) or (main_id is None) or (dessert_id is None):
        return str(-1), str(400)
    elif name_to_id_generator(meal_name, meals_collection.find()) != -1:
        return str(-2), str(400)
    else:
        appetizer, main, dessert = validate_new_meal(appetizer_id, main_id, dessert_id, dishes_collection.find())
        if (appetizer, main, dessert) == (None, None, None):
            return str(-5), str(404)
        # Creates a new dish and adds it to our RESTful API
        meal_id += 1

        # Sum of dishes' values in the meal
        calories = main[CAL] + appetizer[CAL] + dessert[CAL]
        sodium = main[SODIUM] + appetizer[SODIUM] + dessert[SODIUM]
        sugar = main[SUGAR] + appetizer[SUGAR] + dessert[SUGAR]
        meal = {
            NAME: meal_name,
            ID: str(meal_id),
            APPETIZER: appetizer_id,
            MAIN: main_id,
            DESSERT: dessert_id,
            CAL: calories,
            SODIUM: sodium,
            SUGAR: sugar
        }
        meals_collection.insert_one(meal)
        return str(meal_id), str(201)


def validate_new_meal(appetizer: int, main: int, dessert: int, dishes: pymongo.cursor.Cursor) -> tuple:
    """
    :param appetizer: ID of some appetizer that is supposed to be in the dishes collection
    :param main: ID of some main that is supposed to be in the dishes collection
    :param dessert: ID of some dessert that is supposed to be in the dishes collection
    :param dishes: A collection of dishes from MongoDB
    :return: boolean value
    """
    appetizer_instance = None
    main_instance = None
    dessert_instance = None
    for dish in dishes:
        if str(appetizer) == dish[ID]:
            appetizer_instance = dish
        elif str(main) == dish[ID]:
            main_instance = dish
        elif str(dessert) == dish[ID]:
            dessert_instance = dish
        if appetizer_instance and main_instance and dessert_instance:
            return appetizer_instance, main_instance, dessert_instance
    return None, None, None


@app.route('/meals', methods=['GET'])
def get_meals() -> flask.Response:
    """
    GET request of /meals endpoint
    Also supports `GET /meals http://0.0.0.0:port/meals?<diet>` where <diet> gives the name of the diet.
    The response are all those meals that conform to the diets.
    If the <diet> specifies `cal=num1, sodium=num2, sugar=num3`
    then all the meals returned have calories <= num1, sodium <= num2, and sugar <=num3.
    :return: JSON file of all meals. Status code to return was not written in the assignment
    """
    global meals_collection
    # Get new diet from JSON
    diet_name = request.args.get('diet', None, type=str)
    if diet_name is None:
        meals = [meal for meal in list(meals_collection.find())]
        # Convert ObjectId (`_id`) values to strings
        for meal in meals:
            meal['_id'] = str(meal['_id'])
        return jsonify(meals)
    else:
        response: requests.models.Response = requests.get(f'http://localhost:5002/diets/{diet_name}')
        diets_service_response: dict = json.loads(response.content)
        if CAL not in diets_service_response.keys():
            raise ValueError('ERROR: Diet JSON does not contain `cal` value!')
        elif SODIUM not in diets_service_response.keys():
            raise ValueError('ERROR: Diet JSON does not contain `sodium` value!')
        elif SUGAR not in diets_service_response.keys():
            raise ValueError('ERROR: Diet JSON does not contain `sugar` value!')
        cal_max = diets_service_response[CAL]
        sodium_max = diets_service_response[SODIUM]
        sugar_max = diets_service_response[SUGAR]
        # 4. Filter the meals dictionary by diet maximum cal rate, maximum sodium rate, and maximum sugar rate
        filtered_meals = [meal for meal in meals_collection.find() if
                          (meal[CAL] <= cal_max) and
                          (meal[SODIUM] <= sodium_max) and
                          (meal[SUGAR] <= sugar_max)
                          ]
        for meal in filtered_meals:
            meal['_id'] = str(meal['_id'])
        return jsonify(filtered_meals)


@app.route('/meals/<meal_request>', methods=['GET'])
def get_meal(meal_request: str) -> flask.Response:
    """
    GET request of /meals endpoint. Returns a meal with the given ID or name
    :param meal_request: Query param for GET request of /meals endpoint. It may be an ID or a name of a given meal.
    :return: JSON of the meal for valid request, (-1, 400) if the query parameter is empty, (-5, 404) if the ID or name
    don't exist
    """
    global meals_collection
    if (meal_request is None) or (meal_request == ""):
        return str(-1), str(400)
    elif meal_request.isdigit() is True:
        meal = int(meal_request)
        if validate_instance_id(meal, meals_collection) is False:
            return str(-5), str(404)
    else:
        meal_name = meal_request
        meal = name_to_id_generator(meal_name, meals_collection.find())
        if meal == -1:
            return str(-5), str(404)

    res_meal = list(meals_collection.find({ID: str(meal)}))[0]
    res_meal['_id'] = str(res_meal['_id'])
    return jsonify(res_meal), str(200)


@app.route('/meals/<meal_request>', methods=['DELETE'])
def delete_meal(meal_request: str) -> flask.Response:
    """
    DELETE request of /meals endpoint. Returns a meal with the given ID or name
    :param meal_request: Query param for DELETE request of /meals endpoint. It may be an ID or a name of a given meal.
    :return: JSON of the meal for valid request, (-1, 400) if the query parameter is empty, (-5, 404) if the ID or name
    don't exist
    """
    global meals_collection
    if (meal_request is None) or (meal_request == ""):
        return str(-1), str(400)
    elif meal_request.isdigit() is True:
        meal = int(meal_request)
        if validate_instance_id(meal, meals_collection) is False:
            return str(-5), str(404)
    else:
        dish_name = meal_request
        meal = name_to_id_generator(dish_name, meals_collection.find())
        if meal == -1:
            return str(-5), str(404)
    # Remove meal from meals
    query = {ID: str(meal)}
    meals_collection.find_one_and_delete(query)

    return str(meal), str(200)


@app.route('/meals/<meal_request>', methods=['PUT'])
def update_meal(meal_request: str) -> flask.Response:
    """
    PUT request of /meals endpoint. Returns a meal with the given ID or name
    :param meal_request: Query param for PUT request of /meals endpoint. It is an ID of a given meal.
    :return: JSON of the meal for valid request, (-1, 400) if the query parameter is empty, (-5, 404) if the ID or name
    don't exist
    """
    global meals_collection
    if (meal_request is None) or (meal_request == ""):
        return str(-1), str(400)
    elif meal_request.isdigit() is True:
        meal = int(meal_request)
        if validate_instance_id(meal, meals_collection) is False:
            return str(-5), str(404)
    else:
        return str(-5), str(404)

    # Get new meal values from JSON
    meal_name = request.json.get(NAME, None)
    appetizer_id = request.json.get(APPETIZER, None)
    main_id = request.json.get(MAIN, None)
    dessert_id = request.json.get(DESSERT, None)
    if (meal_name is None) or (appetizer_id is None) or (main_id is None) or (dessert_id is None):
        return str(-1), str(400)
    else:
        query = {ID: str(meal)}
        appetizer, main, dessert = validate_new_meal(appetizer_id, main_id, dessert_id, dishes_collection.find())
        if (appetizer, main, dessert) == (None, None, None):
            return str(-5), str(404)
        # Sum of dishes' values in the meal
        calories = appetizer[CAL] + main[CAL] + dessert[CAL]
        sodium = appetizer[SODIUM] + main[SODIUM] + dessert[SODIUM]
        sugar = appetizer[SUGAR] + main[SUGAR] + dessert[SUGAR]

        # Update dictionary
        update = {'$set': {NAME: meal_name, CAL: calories, SODIUM: sodium, SUGAR: sugar}}

        if meals_collection.update_one(query, update).modified_count == 0:
            # This was not asked in the forum but if no changes were made, we get a conflict
            return str(meal), str(409)
        else:
            return str(meal), str(200)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5001)
