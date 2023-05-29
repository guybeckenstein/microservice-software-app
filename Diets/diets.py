from flask import Flask, jsonify, request
#from pymongo import MongoClient  # TODO: make this API interact with the MongoDB microservice

# Constant global Variables
NAME = 'name'               # For diets
MESSAGE = 'message'         # For responses
# Global variables
app = Flask(__name__)
diets = []


@app.route('/diets', methods=['POST'])
def create_diet():
    new_diet = request.get_json()
    diet_names = [diet[NAME] for diet in diets]

    if new_diet[NAME] in diet_names:
        return jsonify({MESSAGE: 'Diet with the same name already exists'}), str(400)

    diets.append(new_diet)
    return jsonify({MESSAGE: 'Diet created successfully'}), str(201)


@app.route('/diets', methods=['GET'])
def get_diets():
    return jsonify(diets)


@app.route('/diet/<name>', methods=['GET'])
def get_diet_by_name(name):
    for diet in diets:
        if diet[NAME] == name:
            return jsonify(diet), str(200)
    return jsonify({MESSAGE: 'Diet not found'}), str(404)


if __name__ == '__main__':
    # With debug=True we can see updates on page after refreshing (F5) without initializing new server again
    app.run(host='0.0.0.0', debug=True, port=5002)