from flask import Blueprint, session, redirect, request, render_template, current_app

from utils.UseDatabase import UseDatabase
from utils.qb import QB


def check_auth(url):
    def decorated_arg(fn):
        def decorated(*args, **kwargs):
            if not has_active_session():
                return redirect(url)

            return fn(*args, **kwargs)

        decorated.__name__ = fn.__name__ + '_decorated'

        return decorated

    return decorated_arg


def has_active_session():
    return 'user' in session


def get_current_role():
    if 'user' in session and 'role_name' in session['user']:
        return session['user']['role_name']
    else:
        return None


def get_current_user_id():
    if 'user' in session and 'user_id' in session['user']:
        return session['user']['user_id']
    else:
        return None


def create_auth_blueprint(main_page):
    auth_blueprint = Blueprint('auth_blueprint', __name__, template_folder='templates')

    @auth_blueprint.route('/', methods=['GET', 'POST'])
    def auth_blueprint_route_root():
        if has_active_session():
            return redirect(main_page)

        if request.method == 'GET':
            return render_template('auth.html')

        elif request.method != 'POST':
            return 'Unknown request'

        username = request.form.get('username')
        password = request.form.get('password')

        if not username:
            return render_template('auth.html', message="Имя пользователя не заполнено!")

        if not password:
            return render_template('auth.html', message="Пароль не заполнен!")

        # Здесь надо заветси еще одного пользователя
        with UseDatabase(current_app.config['db']['guest']) as connection:
            find_user_query = QB() \
                .select('*') \
                .from_table('user') \
                .where('login = "{}" AND password = "{}"'.format(username, password)) \
                .build()

            connection.execute(find_user_query)
            result = connection.fetchall()

            has_user = len(result) > 0

            if not has_user:
                return render_template('auth.html', message="Некорректные данные!")

            found_user = result[0]

            user_id = found_user[0]
            role_id = found_user[1]

            get_role_name_query = QB() \
                .select('role_name') \
                .from_table('role') \
                .where('role_id = {}'.format(role_id)) \
                .build()

            connection.execute(get_role_name_query)
            result = connection.fetchall()

            role_name = result[0][0]

            if not role_name:
                return render_template('auth.html', message="Привилегии пользователя не определены!")

            session['user'] = {
                'user_id': user_id,
                'role_name': role_name
            }

            return redirect(main_page)

    @auth_blueprint.route('/logout', methods=['GET'])
    def auth_blueprint_route_logout():
        if 'user' in session:
            session.pop('user')

        return redirect(main_page)

    return auth_blueprint
