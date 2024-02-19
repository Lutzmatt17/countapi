from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import redis
import uuid

app = Flask(__name__)
CORS(app)

redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

@app.route('/create', methods=['GET'])
@cross_origin
def create_namespace():
    namespace = request.args.get('namespace', type=str)
    if not namespace:
        return jsonify({"error": "Namespace parameter is required"}), 400

    key = request.args.get('key', type=str)

    if not key:
        key = str(uuid.uuid4())

    value = 0

    redis_client.hset(namespace, key, value)

    return jsonify({"namespace": namespace, "key": key, "value": value}), 201

@app.route('/hit/<namespace>/<key>', methods=['GET'])
@cross_origin
def hit_namespace_key(namespace, key):
    new_value = redis_client.hincrby(namespace, key, 1)

    callback = request.args.get('callback', type=str)
    if not callback:
        return jsonify({"error": "Callback parameter is required"}), 400

    response = f'{callback}({{"namespace": "{namespace}", "key": "{key}", "new_value": {new_value}}});'

    return app.response_class(response, content_type='application/javascript')

if __name__ == '__main__':
    app.run(debug=True)