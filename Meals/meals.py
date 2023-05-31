from typing import Tuple

from flask import Flask, request, jsonify
import flask
import json
import requests
from pymongo import MongoClient  # TODO: make this API interact with the MongoDB microservice

# Constant global Variables
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
dishes = dict()             # For dishes
dish_id = 0                 # For dishes
meals = dict()              # For meals
meal_id = 0                 # For meals

API_KEY = 'MktCMe6vJqb/xCbZ10IBgA==5utKBDSANyr1ZXUN'


def calculate_portions_values_sum(response_json: dict) -> Tuple[float, float, float, float]:
    """
    The purpose of this function is to avoid exception for edge cases as mentioned here:
    https://mama.mta.ac.il/mod/forum/discuss.php?d=9130
    :param response_json: The JSON response of our request
    :return: The function calculates the sum of the values of the portions, and return these values - calories, serving
    size, sodium, sugar
    """
    # Return each sum
    return response_json['calories'], response_json['serving_size_g'], response_json['sodium_mg'], response_json['sugar_g']


# Dishes
@app.route('/dishes', methods=['POST'])
def create_dish() -> flask.Response:
    """
    POST request of /dishes endpoint. Adds a dish with the given name in the JSONic body
    :return: ID of the new dish, if there are no edge cases
    """
    global dish_id
    # Bad request: request content-type is not application/json
    if request.content_type != 'application/json':
        return str(0), str(415)

    dish_name = request.json.get(NAME, None)
    if dish_name is None:                # Bad request: NAME parameter was not specified
        return str(-1), str(400)
    response_json: dict = get_dish_nutrition_info(dish_name)
    if response_json == {False}:     # Bad request: does not recognize this dish name
        return str(-3), str(400)
    if response_json == {True}:      # Bad request: not reachable or some other server error
        return str(-4), str(400)
    response_id, response_code = validate_dish_json_parameters(dish_name, response_json)
    if response_id is not None:
        return str(response_id), str(response_code)
    else:
        # Creates a new dish and adds it to our RESTful API
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
        dishes[str(dish_id)] = dish
        return str(dish_id), str(response_code)


def validate_dish_json_parameters(dish_name: str, response_json: dict) -> Tuple:
    """
    :param dish_name: Name of the dish we are adding, given in the original request. Type: str
    :param response_json: Response list of the original request (including query parameter NAME), given by Ninjas API
    :return: (None, 201) if the request is valid, (-2, 400) if the dish already exists, (-3, 400) if the dish does not
    exist in Ninjas API
    """
    if name_to_id_generator(dish_name, dishes) != -1:
        return -2, 400  # Bad request: dish of given name already exists
    elif response_json is None:
        return -3, 400  # Bad request: api.api-ninjas.com/v1/nutrition does not recognize this dish name
    return None, 201


def name_to_id_generator(dish_to_add_name: str, dishes: dict) -> int:
    """
    :param dish_to_add_name: Name of the dish or meal we are adding, given in the original request. Type: str
    :param dishes: A dictionary of dictionaries, each value represents a dish or a meal. Type: dict
    :return: Integer value of a dish or meal ID - positive if found, -1 if not
    """
    for dish in dishes.values():
        if dish[NAME] == dish_to_add_name:
            return dish[ID]
    return -1


def get_dish_nutrition_info(dish_name: str) -> dict:
    """
    :param dish_name: Name of the dish we are adding, given in the original request. Type: str
    :return: Response for the original request (including quey parameter NAME), given by Ninjas API. Type: JSON
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
    return jsonify(dishes)


@app.route('/dishes/<dish_request>', methods=['GET'])
def get_dish(dish_request: str) -> flask.Response:
    """
    GET request of /dishes endpoint. Returns a dish with the given ID or name
    :param dish_request: Query parameter for GET request of /dishes endpoint. It may be an ID or a name of a given dish.
    :return: JSON of the dish for valid request, (-1, 400) if the query parameter is empty, (-5, 404) if the ID or name
    don't exist
    """
    global dishes, dish_id
    if (dish_request is None) or (dish_request == ""):
        # If neither the dish ID nor a dish name is specified, the GET or DELETE
        # request returns the response -1 with error code 400 (Bad request).
        return str(-1), str(400)
    elif dish_request.isdigit() is True:
        dish = int(dish_request)
        if str(dish) not in dishes:
            # # If dish name or dish ID does not exist,
            # the GET or DELETE request returns the response -5 with error code 404 (Not Found)
            return str(-5), str(404)
    else:
        dish_name = dish_request
        dish = name_to_id_generator(dish_name, dishes)
        if dish == -1:
            # # If dish name or dish ID does not exist,
            # the GET or DELETE request returns the response -5 with error code 404 (Not Found)
            return -5, 404
    return jsonify(dishes[str(dish)]), str(200)


@app.route('/dishes/<dish_request>', methods=['DELETE'])
def delete_dish(dish_request: str) -> flask.Response:
    """
    DELETE request of /dishes endpoint. Deletes a dish with the given ID or name
    :param dish_request: Query param for DELETE request of /dishes endpoint
    :return: ID of the dish for valid request, (-1, 400) if the query parameter is empty, (-5, 404) if the ID or name
    don't exist
    """
    global dishes, dish_id
    if (dish_request is None) or (dish_request == ""):
        # If neither the dish ID nor a dish name is specified, the GET or DELETE
        # request returns the response -1 with error code 400 (Bad request).
        return str(-1), str(400)
    elif dish_request.isdigit() is True:
        dish = int(dish_request)
        if str(dish) not in dishes:
            # # If dish name or dish ID does not exist,
            # the GET or DELETE request returns the response -5 with error code 404 (Not Found)
            return str(-5), str(404)
    else:
        dish_name = dish_request
        dish = name_to_id_generator(dish_name, dishes)
        if dish == -1:
            # # If dish name or dish ID does not exist,
            # the GET or DELETE request returns the response -5 with error code 404 (Not Found)
            return str(-5), str(404)

    # Set the dish to null in all meals if it is part of a meal
    dish = str(dish_id)
    for meal in meals.values():
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
            meals[str(meal_id)][CAL] -= dishes[dish][CAL]
            meals[str(meal_id)][SODIUM] -= dishes[dish][SODIUM]
            meals[str(meal_id)][SUGAR] -= dishes[dish][SUGAR]
    # Remove dish from dishes
    dishes.pop(dish)

    return dish, 200


# Meals
@app.route('/meals', methods=['POST'])
def create_meal() -> flask.Response:
    """
    A meal object is different from a dish object. While it also has the "cal", "sodium" and "sugar" fields,
    it does not have the serving "size" field.
    POST request of /meals endpoint. Adds a meal with the given name and dishes in the JSONic body
    :return: an ID of our new meal, if there are no edge-cases
    """
    global meal_id
    # Bad request: request content-type is not application/json
    if request.content_type != 'application/json':
        return str(0), str(415)

    # Get new meal values from JSON
    meal_name = request.json.get(NAME, None)
    appetizer_id = request.json.get(APPETIZER, None)
    main_id = request.json.get(MAIN, None)
    dessert_id = request.json.get(DESSERT, None)
    # Bad request: one of the required parameters was not specified correctly
    if (meal_name is None) or (appetizer_id is None) or (main_id is None) or (dessert_id is None):
        return str(-1), str(400)
    # Bad request: a meal of the given name already exists
    if name_to_id_generator(meal_name, meals) != -1:
        return str(-2), str(400)

    # Validate dishes
    if (str(appetizer_id) not in dishes) or (str(main_id) not in dishes) or (str(dessert_id) not in dishes):
        return str(-5), str(404)

    # Creates a new dish and adds it to our RESTful API
    meal_id += 1

    # New dishes in meal
    str_appetizer = str(appetizer_id)
    str_main = str(main_id)
    str_dessert = str(dessert_id)

    # Sum of dishes' values in the meal
    calories = dishes[str_main][CAL] + dishes[str_appetizer][CAL] + dishes[str_dessert][CAL]
    sodium = dishes[str_main][SODIUM] + dishes[str_appetizer][SODIUM] + dishes[str_dessert][SODIUM]
    sugar = dishes[str_main][SUGAR] + dishes[str_appetizer][SUGAR] + dishes[str_dessert][SUGAR]
    meal = {
        NAME: meal_name,
        ID: meal_id,
        APPETIZER: appetizer_id,
        MAIN: main_id,
        DESSERT: dessert_id,
        CAL: calories,
        SODIUM: sodium,
        SUGAR: sugar
    }
    meals[str(meal_id)] = meal
    return str(meal_id), str(201)


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

    # Get new meal values from JSON
    diet_name = request.args.get('diet', None, type=str)
    if diet_name is None:
        return jsonify(meals)
    else:
        # 1. Connect to 'Diets API'
        # 2. Make a request: `GET /diet/<diet_name>`
        # 3. Get the relevant values from the JSON that was returned from the GET request
        # Get diet values from JSON
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
        filtered_meals = {
            meal_id: meal_details for meal_id, meal_details in meals.items() if
            (meal_details[CAL] <= cal_max) and
            (meal_details[SODIUM] <= sodium_max) and
            (meal_details[SUGAR] <= sugar_max)
        }
        return jsonify(filtered_meals)


@app.route('/meals/<meal_request>', methods=['GET'])
def get_meal(meal_request: str) -> flask.Response:
    """
    GET request of /meals endpoint. Returns a meal with the given ID or name
    :param meal_request: Query param for GET request of /meals endpoint. It may be an ID or a name of a given meal.
    :return: JSON of the meal for valid request, (-1, 400) if the query parameter is empty, (-5, 404) if the ID or name
    don't exist
    """
    global meals
    if (meal_request is None) or (meal_request == ""):
        # If neither the meal ID nor a meal name is specified, the GET or DELETE
        # request returns the response -1 with error code 400 (Bad request).
        return str(-1), str(400)
    elif meal_request.isdigit() is True:
        meal_id = int(meal_request)
        if str(meal_id) not in meals:
            # # If meal name or meal ID does not exist,
            # the GET or DELETE request returns the response -5 with error code 404 (Not Found)
            return str(-5), str(404)
    else:
        meal_name = meal_request
        meal_id = name_to_id_generator(meal_name, meals)
        if meal_id == -1:
            # # If meal name or meal ID does not exist,
            # the GET or DELETE request returns the response -5 with error code 404 (Not Found)
            return str(-5), str(404)
    return jsonify(meals[str(meal_id)]), str(200)


@app.route('/meals/<meal_request>', methods=['DELETE'])
def delete_meal(meal_request: str) -> flask.Response:
    """
    DELETE request of /meals endpoint. Returns a meal with the given ID or name
    :param meal_request: Query param for DELETE request of /meals endpoint. It may be an ID or a name of a given meal.
    :return: JSON of the meal for valid request, (-1, 400) if the query parameter is empty, (-5, 404) if the ID or name
    don't exist
    """
    global meals
    if (meal_request is None) or (meal_request == ""):
        # If neither the meal ID nor a meal name is specified, the GET or DELETE
        # request returns the response -1 with error code 400 (Bad request).
        return str(-1), str(400)
    elif meal_request.isdigit() is True:
        meal_id = int(meal_request)
        if str(meal_id) not in meals:
            # # If meal name or meal ID does not exist,
            # the GET or DELETE request returns the response -5 with error code 404 (Not Found)
            return str(-5), str(404)
    else:
        dish_name = meal_request
        meal_id = name_to_id_generator(dish_name, meals)
        if meal_id == -1:
            # # If meal name or meal ID does not exist,
            # the GET or DELETE request returns the response -5 with error code 404 (Not Found)
            return str(-5), str(404)
    meals.pop(str(meal_id))

    return str(meal_id), str(200)


@app.route('/meals/<meal_request>', methods=['PUT'])
def update_meal(meal_request: str) -> flask.Response:
    """
    PUT request of /meals endpoint. Returns a meal with the given ID or name
    :param meal_request: Query param for PUT request of /meals endpoint. It is an ID of a given meal.
    :return: JSON of the meal for valid request, (-1, 400) if the query parameter is empty, (-5, 404) if the ID or name
    don't exist
    """
    global meals
    if (meal_request is None) or (meal_request == ""):
        # If neither the meal ID nor a meal name is specified, the GET or DELETE
        # request returns the response -1 with error code 400 (Bad request).
        return str(-1), str(400)
    elif meal_request.isdigit() is True:
        meal_id = int(meal_request)
        if str(meal_id) not in meals:
            # # If meal name or meal ID does not exist,
            # the GET or DELETE request returns the response -5 with error code 404 (Not Found)
            return str(-5), str(404)
    else:
        # # If meal name or meal ID does not exist,
        # the GET or DELETE request returns the response -5 with error code 404 (Not Found)
        return str(-5), str(404)

    # Get new meal values from JSON
    meal_name = request.json.get(NAME, None)
    appetizer_id = request.json.get(APPETIZER, None)
    main_id = request.json.get(MAIN, None)
    dessert_id = request.json.get(DESSERT, None)
    # Bad request: one of the required parameters was not specified correctly
    if (meal_name is None) or (appetizer_id is None) or (main_id is None) or (dessert_id is None):
        return str(-1), str(400)

    # Validate dishes
    if (str(appetizer_id) not in dishes) or (str(main_id) not in dishes) or (str(dessert_id) not in dishes):
        return str(-5), str(404)

    # New dishes in meal or new dish name
    meals[str(meal_id)][NAME] = meal_name
    meals[str(meal_id)][APPETIZER] = appetizer_id
    meals[str(meal_id)][MAIN] = main_id
    meals[str(meal_id)][DESSERT] = dessert_id

    # Sum of dishes' values in the meal
    calories = dishes[str(appetizer_id)][CAL] + dishes[str(main_id)][CAL] + dishes[str(dessert_id)][CAL]
    sodium = dishes[str(appetizer_id)][SODIUM] + dishes[str(main_id)][SODIUM] + dishes[str(dessert_id)][SODIUM]
    sugar = dishes[str(appetizer_id)][SUGAR] + dishes[str(main_id)][SUGAR] + dishes[str(dessert_id)][SUGAR]

    # Update dictionary
    meals[str(meal_id)][CAL] = calories
    meals[str(meal_id)][SODIUM] = sodium
    meals[str(meal_id)][SUGAR] = sugar
    return str(meal_id), str(200)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5001)
