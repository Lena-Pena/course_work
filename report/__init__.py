from flask import Blueprint, render_template, request, current_app, redirect

from auth import check_auth, get_current_role
from utils import make_dict_list_from_rows
from utils.UseDatabase import UseDatabase, DBConnectionError, DBCredentialError, DBBaseError, DBSQLError
from utils.decorators import allow_roles, allow_methods


def redirect_to_root():
    return redirect('/report/')


report_blueprint = Blueprint('report_blueprint', __name__, template_folder='templates')


@report_blueprint.route('/')
@check_auth
@allow_roles(['admin'])
def report_blueprint_root():
    return render_template('report_root.html')


@report_blueprint.route('/result', methods=['POST'])
@check_auth
@allow_methods(['POST'], redirect_to_root)
@allow_roles(['admin'])
def report_blueprint_root():
    current_role = get_current_role()
    year = request.form.get('year')

    try:
        with UseDatabase(current_app.config['db'][current_role]) as cursor:
            call_staff_turnover_query = f'call kursach.staff_turnover(\'{year}\')'
            get_staff_turnover_records_count_query = f'select COUNT(*) as count from staff_turnover where st_year = {year}'
            get_staff_turnover_records_query = f'select * from staff_turnover where st_year = {year}'

            cursor.execute(get_staff_turnover_records_count_query)
            result = make_dict_list_from_rows(cursor)

            if not result[0]['count']:
                cursor.execute(call_staff_turnover_query)

            cursor.execute(get_staff_turnover_records_query)
            records = make_dict_list_from_rows(cursor)

            return render_template('report_result.html',
                                   records=records,
                                   year=year)
    except DBConnectionError as e:
        return 'Произошла ошибка соединения'
    except DBCredentialError as e:
        return 'Не удается войти в бд'
    except DBBaseError as e:
        return 'Произошла непредвиденная ошибка бд'
    except DBSQLError as e:
        return 'Ошибка базы данных'

