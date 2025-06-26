from flask import Flask, request, jsonify, render_template
from message_queue  import MessageQueue
import os 


app = Flask(__name__)
mq = MessageQueue(os.environ["REDIS_URL"])



@app.route("/")
def home(): 
    return render_template("index.html")

@app.route("/produce", methods=["POST"])
def produce():
    data = request.get_json()
    queue = data.get("queue")
    message = data.get("message")
    if not queue or not message:
        return jsonify({"error": "Missing 'queue' or 'message'"}), 400

    msg_id = mq.produce(queue, message)
    return jsonify({"message_id": msg_id}), 200

@app.route("/consume", methods=["GET"])
def consume():
    queue = request.args.get("queue")
    if not queue:
        return jsonify({"error": "Missing 'queue' parameter"}), 400

    result = mq.consume(queue)
    if result is None:
        return jsonify({"message": None}), 200
    return jsonify(result), 200

@app.route("/ack", methods=["POST"])
def ack():
    data = request.get_json()
    queue = data.get("queue")
    msg_id = data.get("id")
    if not queue or not msg_id:
        return jsonify({"error": "Missing 'queue' or 'id'"}), 400

    success = mq.ack(queue, msg_id)
    return jsonify({"success": success}), 200

if __name__ == "__main__":
    app.run(debug=True)
