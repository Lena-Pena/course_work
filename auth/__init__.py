from flask import Blueprint, session, redirect, request, render_template, current_app

from utils.UseDatabase import UseDatabase, DBConnectionError, DBCredentialError, DBBaseError, DBSQLError


# Проверить, если есть актинвая сессия, то продолжить,
# иначе - перенаправить на /auth
def check_auth(fn):
    def decorated(*args, **kwargs):
        if not has_active_session():
            return redirect('/auth')

        return fn(*args, **kwargs)

    decorated.__name__ = fn.__name__ + '_decorated_by_check_auth'

    return decorated


# Есть ли запись о пользователе в сессии
def has_active_session():
    return 'user' in session


# Получить роль текущего пользователя
def get_current_role():
    if 'user' in session and 'role_name' in session['user']:
        return session['user']['role_name']
    else:
        return None


# Получить ID текущего пользователя
def get_current_user_id():
    if 'user' in session and 'user_id' in session['user']:
        return session['user']['user_id']
    else:
        return None


auth_blueprint = Blueprint('auth_blueprint', __name__, template_folder='templates')


# /auth
@auth_blueprint.route('/', methods=['GET', 'POST'])
def auth_blueprint_route_root():
    if has_active_session():
        return redirect('/menu')

    if request.method == 'GET':
        return render_template('auth.html')

    username = request.form.get('username')
    password = request.form.get('password')

    if not username:
        return render_template('auth.html', message="Имя пользователя не заполнено!")

    if not password:
        return render_template('auth.html', message="Пароль не заполнен!")

    # Здесь надо заветси еще одного пользователя
    try:
        with UseDatabase(current_app.config['db']['guest']) as cursor:
            find_user_query = f"""
            SELECT * FROM user WHERE login = "{username}" AND password = "{password}" 
            """

            cursor.execute(find_user_query)
            result = cursor.fetchall()

            has_user = len(result) > 0

            if not has_user:
                return render_template('auth.html', message="Некорректные данные!")

            user_id = result[0][0]
            role_id = result[0][1]

            get_role_name_query = f"""
            select role_name from role where role_id = {role_id}
            """

            cursor.execute(get_role_name_query)
            result = cursor.fetchall()

            has_role = len(result) > 0

            if not has_role:
                return render_template('auth.html', message="Привилегии пользователя не определены!")

            role_name = result[0][0]

            session['user'] = {
                'user_id': user_id,
                'role_name': role_name
            }

            return redirect('/menu')
    except DBConnectionError as e:
        return 'Произошла ошибка соединения'
    except DBCredentialError as e:
        return 'Не удается войти в бд'
    except DBBaseError as e:
        return 'Произошла непредвиденная ошибка бд'
    except DBSQLError as e:
        return 'Ошибка базы данных'


@auth_blueprint.route('/logout', methods=['GET'])
def auth_blueprint_route_logout():
    if 'user' in session:
        session.pop('user')

    return redirect('/auth')
