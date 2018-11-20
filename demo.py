# -*- coding:utf-8 -*-


from flask import Flask, make_response, request, render_template
from flask_bootstrap import Bootstrap

app = Flask(__name__)
bootstrap = Bootstrap(app)
@app.route('/')
def index():
    user_agent = request.headers.get('User-Agent')
    return render_template('index.html',ua=user_agent)

@app.route('/user/<name>') 
def user(name):
    return render_template('user.html', name=name)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('404.html'), 500

if '__main__' == __name__:
	app.run()
