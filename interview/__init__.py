from flask import Blueprint, request, redirect, current_app, render_template, session

from auth import get_current_role, get_current_user_id, check_auth
from utils.UseDatabase import UseDatabase

interview_blueprint = Blueprint('interview_blueprint', __name__, template_folder='templates')


# noinspection PyUnresolvedReferences
@interview_blueprint.route('/create', methods=['POST', 'GET'])
@check_auth
def interview_blueprint_route_create():
    if request.method == 'GET':
        return render_template('interview_admin_create.html')
    elif request.method == 'POST':
        if 'created_interviews' not in session:
            session['created_interviews'] = []

        interviews = session['created_interviews']
        form = request.form

        if len(interviews):
            new_interview_id = interviews[-1]['id'] + 1
        else:
            new_interview_id = 1

        new_interview = {
            'id': new_interview_id,
            'candidate': {
                'name': form.get('candidate_name'),
                'address': form.get('candidate_address'),
                'gender': form.get('candidate_gender'),
                'age': form.get('candidate_age')
            },
            'interview': {
                'v_id': form.get('v_id'),
                'salary': form.get('salary'),
                'iv_date': form.get('iv_date'),
                'dep_number': form.get('dep_number'),
                'emp_id': form.get('emp_id')
            }
        }

        interviews.append(new_interview)
        # Нужно переприсваивать
        session['created_interviews'] = interviews

        return redirect('/interview/created')


@interview_blueprint.route('/delete', methods=['POST'])
@check_auth
def interview_blueprint_route_delete():
    if request.method != 'POST':
        return 'Unknown action'

    interviews = session['created_interviews']
    interview_to_delete_id = int(request.form.get('interview_id'))

    interviews = [
        interview
        for interview in interviews
        if interview['id'] != interview_to_delete_id
    ]

    session['created_interviews'] = interviews

    return redirect('/interview/created')


# noinspection PyUnresolvedReferences
@interview_blueprint.route('/', methods=['GET'])
@check_auth
def interview_blueprint_route_root():
    current_role = get_current_role()

    if request.method != 'GET':
        return 'Unknown action'

    if current_role == 'guest':
        return redirect('/')
    elif current_role == 'admin':
        return render_template('interview_menu.html')
    elif current_role == 'worker':
        return 'Not ready'
    else:
        return 'You are not permitted to see this page'


# noinspection PyUnresolvedReferences
@interview_blueprint.route('/saved', methods=['GET'])
@check_auth
def interview_blueprint_route_saved():
    current_role = get_current_role()

    if request.method != 'GET':
        return 'Unknown action'

    if current_role != 'admin':
        return redirect('/menu')

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
                JOIN vacancy v on interview.v_id = v.v_id
                ORDER BY date;
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

            return render_template(
                'interview_admin_saved.html',
                interviews=interviews
            )
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


# noinspection PyUnresolvedReferences
@interview_blueprint.route('/created', methods=['GET'])
@check_auth
def interview_blueprint_route_created():
    current_role = get_current_role()

    if current_role != 'admin':
        return redirect('/menu')

    if request.method != 'GET':
        return 'Unknown action'

    if 'created_interviews' in session:
        interviews = session['created_interviews']
    else:
        interviews = None

    # Чтобы отобразить сообщение
    interviews = interviews if interviews and len(interviews) > 0 else None

    return render_template('interview_admin_created.html', interviews=interviews)


@interview_blueprint.route('/save', methods=['POST'])
@check_auth
def interview_blueprint_route_save():
    current_role = get_current_role()

    if current_role != 'admin':
        return redirect('/menu')

    if request.method != 'POST':
        return 'Unknown action'

    interviews = session['created_interviews']

    if not interviews:
        return redirect('/interview/created')

    for interview in interviews:
        with UseDatabase(current_app.config['db'][current_role]) as cursor:
            candidate_data = interview['candidate']
            interview_data = interview['interview']

            candidate_address = f"""'{candidate_data['address']}'""" if candidate_data['address'] else 'null'

            create_candidate_query = f"""
            INSERT INTO candidate (name, address, gender, age) VALUES ('{
                candidate_data['name']
            }', {
                candidate_address
            }, '{
                candidate_data['gender']
            }', { candidate_data['age'] })
            """

            cursor.execute(create_candidate_query)

            get_created_candidate_id_query = f"""SELECT MAX(c_id) FROM candidate"""

            cursor.execute(get_created_candidate_id_query)
            result = cursor.fetchall()

            created_candidate_id = int(result[0][0])

            # Вставляем ID созданного кандидата
            create_interview_query = f"""
            INSERT INTO interview (salary, iv_date, c_id, emp_id, v_id, dep_number) VALUES ('{
                interview_data['salary']
            }', '{
                interview_data['iv_date']
            }', {
                created_candidate_id
            }, {
                interview_data['emp_id']
            }, {
                interview_data['v_id']
            }, {
                interview_data['dep_number'] if interview_data['dep_number'] else 'null' 
            })
            """

            cursor.execute(create_interview_query)

    session['created_interviews'] = None

    return redirect('/interview/saved')
