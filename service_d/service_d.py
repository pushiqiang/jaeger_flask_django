import requests
from flask import Flask

from tracing import init_tracer, trace


app = Flask(__name__)
tracer = init_tracer('service_d')


@app.route('/d/')
@trace(tracer)
def index():
    raise Exception('service d raise a exception.')


if __name__ == '__main__':
    app.debug = True
    app.run()
