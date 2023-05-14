from flask import Flask, jsonify, request

app = Flask(__name__)

diets = []


@app.route('/diets', methods=['POST'])
def create_diet():
    new_diet = request.get_json()
    diet_names = [diet['name'] for diet in diets]

    if new_diet['name'] in diet_names:
        return jsonify({'message': 'Diet with the same name already exists'}), 400

    diets.append(new_diet)
    return jsonify({'message': 'Diet created successfully'})


@app.route('/diets', methods=['GET'])
def get_diets():
    return jsonify(diets)


@app.route('/diet/<name>', methods=['GET'])
def get_diet_by_name(name):
    for diet in diets:
        if diet['name'] == name:
            return jsonify(diet)
    return jsonify({'message': 'Diet not found'})


if __name__ == '__main__':
    # With debug=True we can see updates on page after refreshing (F5) without initializing new server again
    app.run(host='0.0.0.0', debug=True, port=5002)
