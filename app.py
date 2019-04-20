from flask import Flask
from flask import jsonify

app = Flask(__name__)

@app.route('/')
def hello():
    data = {'message': 'hi there'}
    return jsonify(data)

if __name__ == '__main__':
    app.run()