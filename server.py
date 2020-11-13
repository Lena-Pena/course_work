import os

from flask import Flask, render_template, redirect

from auth import create_auth_blueprint, has_active_session
from menu import menu_blueprint
from utils.generate_form import generate_form
import json

app = Flask(__name__, template_folder="templates")

app.config['db'] = json.load(open('db.config.json'))

auth_blueprint = create_auth_blueprint(main_page='/menu')

app.register_blueprint(auth_blueprint, url_prefix='/auth')
app.register_blueprint(menu_blueprint, url_prefix='/menu')

app.secret_key = os.urandom(16)


@app.route('/')
def app_route_root():
    if has_active_session():
        return redirect('/menu')
    else:
        return redirect('/auth')


if __name__ == '__main__':
    app.run(port="5000", debug=True)
