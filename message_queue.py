import uuid
import redis
import json

class MessageQueue:
    def __init__(self, redis_url):
        self.r = redis.from_url(redis_url, decode_responses=True)

    def _queue_key(self, queue): return f"queue:{queue}"
    def _unacked_key(self, queue): return f"unacked:{queue}"

    def produce(self, queue, message):
        msg_id = str(uuid.uuid4())
        payload = json.dumps({"id": msg_id, "message": message})
        self.r.rpush(self._queue_key(queue), payload)
        return msg_id

    def consume(self, queue):
        item = self.r.lpop(self._queue_key(queue))
        if not item:
            return None
        msg = json.loads(item)
        self.r.hset(self._unacked_key(queue), msg["id"], msg["message"])
        return msg

    def ack(self, queue, msg_id):
        return self.r.hdel(self._unacked_key(queue), msg_id) > 0
