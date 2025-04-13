from flask import Flask, request, jsonify
import time
from collections import defaultdict, deque

app = Flask(__name__)

class SimpleRateLimiter:
    def __init__(self, requests_per_window=1):
        self.requests_per_window = requests_per_window
        self.window_size = 5
        self.user_requests = defaultdict(deque)
    
    def is_allowed(self, user_id):

        current_time = time.time()
        user_history = self.user_requests[user_id]

        # print(user_history)
        # print(user_id)
        # print(current_time)
        
        while user_history and current_time - user_history[0] > self.window_size:
            user_history.popleft()
        
        if len(user_history) < self.requests_per_window:
            user_history.append(current_time)
            return True
        return False

rate_limiter = SimpleRateLimiter()

@app.route('/api/transactions', methods=['POST'])
def process_transaction():
    user_id = request.headers.get('User-ID', request.remote_addr)
    
    if rate_limiter.is_allowed(user_id):

        transaction_data = request.get_json()
        
        return jsonify({
            "status": "success",
            "message": "Transaction processed successfully",
            "transaction_data": transaction_data
        }), 200
    else:
        return jsonify({
            "status": "error",
            "message": "Rate limit exceeded. Try again later."
        }), 429


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)