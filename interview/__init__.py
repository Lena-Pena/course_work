from flask import Blueprint, request, redirect, current_app, render_template

from auth import get_current_role, get_current_user_id, check_auth
from utils.UseDatabase import UseDatabase


def create_interview_blueprint(auth_failed_route, main_page, url_prefix):
    interview_blueprint = Blueprint('interview_blueprint', __name__, template_folder='templates')

    @interview_blueprint.route('/create', methods=['POST', 'GET'])
    @check_auth(auth_failed_route)
    def interview_blueprint_route_create():
        if request.method == 'GET':
            return render_template('interview_admin_create.html', main_page=main_page, url_prefix=url_prefix)
        elif request.method == 'POST':
            return 'Not ready'
        else:
            return 'Unknown action'

    @interview_blueprint.route('/delete', methods=['POST'])
    @check_auth(auth_failed_route)
    def interview_blueprint_route_delete():
        interview_id = request.form.get('interview_id')
        current_role = get_current_role()

        if request.method != 'POST':
            return 'Unknown action'

        return 'Not ready'

    @interview_blueprint.route('/', methods=['GET'])
    @check_auth(auth_failed_route)
    def interview_blueprint_route_root():
        current_role = get_current_role()

        if request.method != 'GET':
            return 'Unknown action'

        if current_role == 'guest':
            return redirect('/')
        elif current_role == 'admin':
            return render_template('interview_menu.html', main_page=main_page, url_prefix=url_prefix)
        elif current_role == 'worker':
            return 'Not ready'
        else:
            return 'You are not permitted to see this page'

    @interview_blueprint.route('/saved', methods=['GET'])
    @check_auth(auth_failed_route)
    def interview_blueprint_route_saved():
        current_role = get_current_role()

        if request.method != 'GET':
            return 'Unknown action'

        if current_role != 'admin':
            return redirect(main_page)

        with UseDatabase(current_app.config['db'][current_role]) as cursor:
            if current_role == 'admin':
                get_interview_query = """
                SELECT
                    iv_id as id,
                    iv_date as date,
                    v.position as vacancy,
                    interview.salary as salary,
                    e.name as employee,
                    c.name as candidate,
                    result
                    FROM interview
                    JOIN candidate c on interview.c_id = c.c_id
                    JOIN employee e on interview.emp_id = e.emp_id
                    JOIN vacancy v on interview.v_id = v.v_id;
                """

                cursor.execute(get_interview_query)
                result = cursor.fetchall()
                column_names = cursor.column_names

                interviews = []

                for row in result:
                    interview = {}

                    for i in range(len(column_names)):
                        interview[column_names[i]] = row[i]

                    interviews.append(interview)

                return render_template('interview_admin_saved.html',
                                       interviews=interviews,
                                       main_page=main_page)
            elif current_role == 'worker':
                # Добавить, чтоб выводились собсеседования конкретного employee
                worker_id = get_current_user_id()

                get_interview_query = """
                SELECT
                    iv_id as id,
                    iv_date as date,
                    v.position as vacancy,
                    salary
                    c.name as candidate
                    result
                    FROM interview
                    JOIN candidate c on interview.c_id = c.c_id
                    JOIN vacancy v on interview.v_id = v.v_id;
                """

                return 'Not ready'
            else:
                return 'Error. You are not permitted to view this page'

    @interview_blueprint.route('/created', methods=['GET'])
    @check_auth(auth_failed_route)
    def interview_blueprint_route_created():
        current_role = get_current_role()

        if current_role != 'admin':
            return redirect(main_page)

        if request.method != 'GET':
            return 'Unknown action'

        return render_template('interview_admin_created.html',
                               main_page=main_page,
                               url_prefix=url_prefix)

    return interview_blueprint
