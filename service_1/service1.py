from flask import Flask, jsonify

from .trace import init_tracer


app = Flask(__name__)
tracer = init_tracer('formatter')


@app.route('/')
def index():
    data = {}
    return jsonify(data)


if __name__ == '__main__':
    app.debug = True # 设置调试模式，生产模式的时候要关掉debug
    app.run()
