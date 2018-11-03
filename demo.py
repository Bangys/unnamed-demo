# -*- coding:utf-8 -*-


from flask import Flask, make_response, request

app = Flask(__name__)

@app.route('/')
def index():
    user_agent = request.headers.get('User-Agent')
    response = make_response("<h1>what's on your mind?</h1>", 666)
    return response


if '__main__' == __name__:
	app.run()