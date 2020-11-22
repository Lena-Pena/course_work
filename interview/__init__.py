from flask import Blueprint, request, redirect, current_app, render_template, session

from auth import get_current_role, get_current_user_id, check_auth
from utils.UseDatabase import UseDatabase
from utils import make_dict_list_from_rows

interview_blueprint = Blueprint('interview_blueprint', __name__, template_folder='templates')


# noinspection PyUnresolvedReferences
@interview_blueprint.route('/appoint', methods=['POST', 'GET'])
@check_auth
def interview_blueprint_route_create():
    if request.method == 'GET':
        return render_template('interview_appoint_admin.html')
    elif request.method == 'POST':
        if 'appointment' not in session:
            session['appointment'] = []

        interviews = session['appointment']
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
        session['appointment'] = interviews

        return redirect('/interview/created')


@interview_blueprint.route('/remove', methods=['POST'])
@check_auth
def interview_blueprint_route_delete():
    if request.method != 'POST':
        return 'Unknown action'

    interviews = session['appointment']
    interview_to_delete_id = int(request.form.get('interview_id'))

    interviews = [
        interview
        for interview in interviews
        if interview['id'] != interview_to_delete_id
    ]

    session['appointment'] = interviews

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
@interview_blueprint.route('/list', methods=['GET'])
@check_auth
def interview_blueprint_route_saved():
    current_role = get_current_role()

    if request.method != 'GET':
        return 'Unknown action'

    if current_role not in ['admin', 'worker']:
        return redirect('/menu')

    with UseDatabase(current_app.config['db'][current_role]) as cursor:
        if current_role == 'admin':
            get_interviews_query = """
            select
                i.iv_id,
                i.salary,
                e.name as employee,
                i.iv_date,
                v.position
            from interview i
            join employee e on e.emp_id = i.emp_id
            join vacancy v on i.v_id = v.v_id
            where iv_id in (select distinct iv_id from interview_result)
            order by i.iv_id
            """

            cursor.execute(get_interviews_query)
            interviews = make_dict_list_from_rows(cursor)

            get_candidates_query = """
            select
                ir.iv_id,
                c.c_id,
                c.name,
                c.age,
                c.gender,
                c.address
            from interview_result ir
            join candidate c on ir.c_id = c.c_id
            order by ir.iv_id;
            """

            cursor.execute(get_candidates_query)
            candidates = make_dict_list_from_rows(cursor)

            for interview in interviews:
                interview['candidates'] = [
                    candidate
                    for candidate in candidates
                    if candidate['iv_id'] == interview['iv_id']
                ]

            return render_template(
                'interview_list_admin.html',
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
@interview_blueprint.route('/appointed', methods=['GET'])
@check_auth
def interview_blueprint_route_created():
    current_role = get_current_role()

    if current_role != 'admin':
        return redirect('/menu')

    if request.method != 'GET':
        return 'Unknown action'

    appointment = session['appointment'] if 'appointment' in session else {}

    current_interview_id = appointment['interview_id'] if 'interview_id' in appointment else None
    candidate_ids = appointment['candidate_ids'] if 'candidate_ids' in appointment else None

    with UseDatabase(current_app.config['db'][current_role]) as cursor:
        get_remain_candidates_query = """
        select c_id, name from candidates
        """

        candidate_ids_query_chunk = ','.join(str(candidate_ids))

        if candidate_ids:
            get_remain_candidates_query += f"""where c_id not in ({candidate_ids_query_chunk})"""

        get_interviews_query = f"""
        select
            i.iv_id,
            i.salary,
            e.name as employee,
            i.iv_date,
            v.position
        from interview i
        join employee e on e.emp_id = i.emp_id
        join vacancy v on i.v_id = v.v_id
        where 
            iv_id not in (select distinct iv_id from interview_result)
        order by i.iv_id;
        """

        cursor.execute(get_remain_candidates_query)
        remaining_candidates = make_dict_list_from_rows(cursor)

        cursor.execute(get_interviews_query)
        interviews = make_dict_list_from_rows(cursor)

        available_interviews = [
            interview
            for interview in interviews
            if interview['iv_id'] != current_interview_id
        ]

        if

        if candidate_ids:
            get_appointed_candidates_details_query = f"""
            select c_id, name, address, gender, age
            from candidates
            where c_id in ({candidate_ids_query_chunk})
            """
            cursor.execute(get_appointed_candidates_details_query)
            appointed_candidates = make_dict_list_from_rows(cursor)
        else:
            appointed_candidates = []

        return render_template('interview_appointed_admin.html',
                               available_interviews=available_interviews,
                               remaining_candidates=remaining_candidates,)


@interview_blueprint.route('/confirm_appointment', methods=['POST'])
@check_auth
def interview_blueprint_route_save():
    current_role = get_current_role()

    if current_role != 'admin':
        return redirect('/menu')

    if request.method != 'POST':
        return 'Unknown action'

    interviews = session['appointment']

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

    session['appointment'] = None

    return redirect('/interview/saved')
