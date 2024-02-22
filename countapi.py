from flask import Flask, request, jsonify
import redis
import uuid
import os

app = Flask(__name__)

#Instantiate upstash redis instance from url connection string.
redis_url = os.getenv("REDIS_URL")
redis_client = redis.from_url(redis_url)

@app.route('/create', methods=['GET'])
def create_namespace():
    """
    Endpoint that allows for the creation of a namespace and key for a counter.
    If a custom key is not specified, one will be randomly generated.

    Returns:
    - A json object that contains the namespace and key that was created, as well as the current value of the counter.
    """
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
def hit_namespace_key(namespace, key):
    """
    Increments the counter value associated with the given namespace and key by 1. 
    Then it returns a callback function that contains the counter value as the response.
    
    Parameters:
    - namespace (str): The namespace of the counter to be incremented.
    - key (str): The key of the counter within the namespace to be incremented.
    
    Returns:
    - A response object with the application/javascript content type. The body of the response is the callback function
      invocation with the updated counter value.
    """
    new_value = redis_client.hincrby(namespace, key, 1)

    callback = request.args.get('callback', type=str)
    if not callback:
        return jsonify({"error": "Callback function is required"}), 400

    response = f'{callback}({{"namespace": "{namespace}", "key": "{key}", "new_value": {new_value}}});'

    return app.response_class(response, content_type='application/javascript')

if __name__ == '__main__':
    app.run(debug=True)
