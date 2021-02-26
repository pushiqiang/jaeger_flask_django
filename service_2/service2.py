from flask import Flask, jsonify

app = Flask(__name__)


@app.route('/')
def index():
    data = {}
    return jsonify(data)


if __name__ == '__main__':
    app.debug = True # 设置调试模式，生产模式的时候要关掉debug
    app.run()
