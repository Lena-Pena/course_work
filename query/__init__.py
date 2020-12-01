from flask import Blueprint, render_template, request, current_app

from auth import check_auth, get_current_role
from utils import make_dict_list_from_rows
from utils.UseDatabase import UseDatabase, DBConnectionError, DBCredentialError, DBBaseError, DBSQLError
from utils.decorators import allow_roles

query_blueprint = Blueprint('query_blueprint', __name__, template_folder='templates')


@query_blueprint.route('/', methods=['GET'])
@check_auth
@allow_roles(['admin', 'worker'])
def query_blueprint_route_root():
    current_role = get_current_role()

    is_admin = current_role == 'admin'

    return render_template('query_root.html',
                           is_admin=is_admin)


@query_blueprint.route('/interviews', methods=['GET', 'POST'])
@check_auth
@allow_roles(['admin'])
def query_blueprint_route_interviews():
    current_role = get_current_role()
    form = request.form if request.method == 'POST' else None

    try:
        with UseDatabase(current_app.config['db'][current_role]) as cursor:
            if form and 'sign' in form.keys():
                sign = form.get('sign')
            else:
                sign = '>'

            if form and 'rating' in form.keys():
                rating = form.get('rating')
            else:
                rating = 0

            get_interviews_query = f"""
            select
               c.c_id as cd_id, c.name as c_name,
               i.iv_id, i.salary as i_salary, iv_date,
               v.v_id, position,
               e.emp_id, e.name as e_name,
               ir.rating, ir.result
            from interview_result ir
            join candidate c on c.c_id = ir.c_id
            join interview i on i.iv_id = ir.iv_id
            join vacancy v on v.v_id = i.v_id
            join employee e on i.emp_id = e.emp_id
            where ir.rating {sign} {rating};
            """

            cursor.execute(get_interviews_query)

            interviews = make_dict_list_from_rows(cursor)

            return render_template('query_interviews.html',
                                   interviews=interviews,
                                   sign=sign,
                                   rating=rating)
    except DBConnectionError as e:
        return 'Произошла ошибка соединения'
    except DBCredentialError as e:
        return 'Не удается войти в бд'
    except DBBaseError as e:
        return 'Произошла непредвиденная ошибка бд'
    except DBSQLError as e:
        return 'Ошибка базы данных'


@query_blueprint.route('/employees', methods=['GET', 'POST'])
@check_auth
@allow_roles(['admin', 'worker'])
def query_blueprint_route_employees():
    current_role = get_current_role()
    form = request.form if request.method == 'POST' else None

    try:
        with UseDatabase(current_app.config['db'][current_role]) as cursor:
            if form and 'year' in form:
                year = form.get('year')
            else:
                year = None

            where_clause_query_chunk = \
                f'and YEAR(layoff_date) = {year}' if year \
                    else ''

            get_employees_query = f"""
            select emp_id, name, salary, education, reception_date, layoff_date
            from employee
            where layoff_date is not null
            {where_clause_query_chunk}
            """

            cursor.execute(get_employees_query)
            emps = make_dict_list_from_rows(cursor)

            return render_template('query_employees.html',
                                   emps=emps,
                                   year=year)
    except DBConnectionError as e:
        return 'Произошла ошибка соединения'
    except DBCredentialError as e:
        return 'Не удается войти в бд'
    except DBBaseError as e:
        return 'Произошла непредвиденная ошибка бд'
    except DBSQLError as e:
        return 'Ошибка базы данных'


@query_blueprint.route('/vacancies', methods=['GET', 'POST'])
@check_auth
@allow_roles(['admin', 'worker'])
def query_blueprint_route_vacancies():
    current_role = get_current_role()
    form = request.form if request.method == 'POST' else None

    try:
        with UseDatabase(current_app.config['db'][current_role]) as cursor:
            if form and 'year' in form:
                year = form.get('year')
            else:
                year = None

            where_clause_query_chunk = \
                f'where YEAR(opening_date) = {year}' if year \
                    else ''

            get_vacancies_query = f"""
            select v_id, position, opening_date, closing_date 
            from vacancy
            {where_clause_query_chunk}
            """

            cursor.execute(get_vacancies_query)
            vacancies = make_dict_list_from_rows(cursor)

            return render_template('query_vacancies.html',
                                   vacancies=vacancies,
                                   year=year)
    except DBConnectionError as e:
        return 'Произошла ошибка соединения'
    except DBCredentialError as e:
        return 'Не удается войти в бд'
    except DBBaseError as e:
        return 'Произошла непредвиденная ошибка бд'
    except DBSQLError as e:
        return 'Ошибка базы данных'
