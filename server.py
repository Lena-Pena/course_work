import json
import os

from flask import Flask, redirect

from auth import create_auth_blueprint, has_active_session
from menu import create_menu_blueprint
from interview import create_interview_blueprint

app = Flask(__name__, template_folder="templates")

app.config['db'] = json.load(open('db.config.json'))

auth_blueprint = create_auth_blueprint(main_page='/menu')
menu_blueprint = create_menu_blueprint(auth_failed_route='/auth')

interview_blueprint = create_interview_blueprint(
    auth_failed_route='/auth',
    main_page='/menu',
    url_prefix='/interview')

app.register_blueprint(auth_blueprint, url_prefix='/auth')
app.register_blueprint(menu_blueprint, url_prefix='/menu')
app.register_blueprint(interview_blueprint, url_prefix='/interview')

app.secret_key = os.urandom(16)


@app.route('/')
def app_route_root():
    if has_active_session():
        return redirect('/menu')
    else:
        return redirect('/auth')


if __name__ == '__main__':
    app.run(port="5000", debug=True)
