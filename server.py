import json
import os

from flask import Flask, redirect

from auth import auth_blueprint, check_auth
from menu import menu_blueprint
from interview import interview_blueprint

app = Flask(__name__, template_folder="templates")

# app.config = {
#  'db': { json-файл с настройками подключения БД }
# }
app.config['db'] = json.load(open('data_files/db.config.json'))

# Регистирурем блюпринты
app.register_blueprint(auth_blueprint, url_prefix='/auth')
app.register_blueprint(menu_blueprint, url_prefix='/menu')
app.register_blueprint(interview_blueprint, url_prefix='/interview')


# Для сессии
app.secret_key = os.urandom(16)


@app.route('/')
@check_auth
def app_route_root():
    return redirect('/menu')


if __name__ == '__main__':
    app.run(port="5000", debug=True)
