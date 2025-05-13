from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello, Flask!"

if __name__ == '__main__':
<<<<<<< HEAD
    app.run(debug=True, host='127.0.0.1', port=5001)
=======
    app.run(debug=True, host='127.0.0.1', port=5001)
>>>>>>> 96cc0499af803d9666e1418f4ea418f22480aae5
