from flask import Blueprint, request, redirect, current_app, render_template, session

from auth import get_current_role, get_current_user_id, check_auth
from utils.UseDatabase import UseDatabase, DBConnectionError, DBCredentialError, DBBaseError, DBSQLError
from utils import make_dict_list_from_rows

interview_blueprint = Blueprint('interview_blueprint', __name__, template_folder='templates')


# noinspection PyUnresolvedReferences
@interview_blueprint.route('/', methods=['GET'])
@check_auth
def interview_blueprint_route_root():
    current_role = get_current_role()

    if request.method != 'GET':
        return 'Unknown action'

    if current_role == 'guest':
        return redirect('/menu')
    elif current_role == 'admin':
        return render_template('interview_menu.html')
    elif current_role == 'worker':
        return redirect('/interview/list')
    else:
        return 'You are not permitted to see this page'


# noinspection PyUnresolvedReferences
@interview_blueprint.route('/list', methods=['GET'])
@check_auth
def interview_blueprint_route_list():
    current_role = get_current_role()

    if request.method != 'GET':
        return 'Unknown action'

    if current_role not in ['admin', 'worker']:
        return redirect('/menu')
    try:
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

                get_interview_query = f"""
                SELECT
                    i.iv_date as date,
                    v.position, 
                    i.salary, 
                    c.name as candidate, 
                    iv.result, 
                    iv.rating 
                from interview_result iv
                join interview i on iv.iv_id = i.iv_id
                join candidate c on iv.c_id = c.c_id
                join employee e on i.emp_id = e.emp_id
                join vacancy v on i.v_id = v.v_id
                where e.emp_id = {worker_id}
                """

                cursor.execute(get_interview_query)
                interviews = make_dict_list_from_rows(cursor)

                return render_template('interview_list_worker.html',
                                       interviews=interviews)
            else:
                return 'Error. You are not permitted to view this page'
    except DBConnectionError as e:
        return 'Произошла ошибка соединения'
    except DBCredentialError as e:
        return 'Не удается войти в бд'
    except DBBaseError as e:
        return 'Произошла непредвиденная ошибка бд'
    except DBSQLError as e:
        return 'Ошибка базы данных'


# noinspection PyUnresolvedReferences
@interview_blueprint.route('/appointed', methods=['GET'])
@check_auth
def interview_blueprint_route_appointed():
    current_role = get_current_role()

    if current_role != 'admin':
        return redirect('/menu')

    if request.method != 'GET':
        return 'Unknown action'

    if 'appointment' not in session:
        session['appointment'] = {
            'interview_id': None,
            'candidate_ids': []
        }

    current_interview_id = session['appointment']['interview_id']
    candidate_ids = session['appointment']['candidate_ids']

    try:
        with UseDatabase(current_app.config['db'][current_role]) as cursor:
            if current_interview_id:
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
                    iv_id = {current_interview_id}
                order by i.iv_id;
                """

                cursor.execute(get_interviews_query)
                result_row = make_dict_list_from_rows(cursor)
                interview = result_row[0] if result_row else None
            else:
                interview = None

            if candidate_ids:
                get_appointed_candidates_query = f"""
                select c_id, name, age, gender, address
                from candidate
                where c_id in ({','.join(str(id) for id in candidate_ids)})
                """

                cursor.execute(get_appointed_candidates_query)
                candidates = make_dict_list_from_rows(cursor)
            else:
                candidates = []
    except DBConnectionError as e:
        return 'Произошла ошибка соединения'
    except DBCredentialError as e:
        return 'Не удается войти в бд'
    except DBBaseError as e:
        return 'Произошла непредвиденная ошибка бд'
    except DBSQLError as e:
        return 'Ошибка базы данных'

    return render_template('interview_appointed_admin.html',
                           interview=interview,
                           candidates=candidates if candidates else None)


@interview_blueprint.route('/appointment/confirm', methods=['POST'])
@check_auth
def interview_blueprint_route_appointment_confirm():
    current_role = get_current_role()

    if current_role != 'admin':
        return redirect('/menu')

    if request.method != 'POST':
        return 'Unknown action'

    if 'appointment' not in session:
        return redirect('/interview/list')

    appointment = session['appointment']
    interview_id = appointment['interview_id']
    candidate_ids = appointment['candidate_ids']

    if not interview_id or not candidate_ids:
        return redirect('/interview/list')

    try:
        with UseDatabase(current_app.config['db'][current_role]) as cursor:
            for candidate_id in candidate_ids:
                appoint_candidates_query = f"""
                insert
                into interview_result (c_id, iv_id)
                values ({candidate_id}, {interview_id})
                """

                cursor.execute(appoint_candidates_query)
    except DBConnectionError as e:
        return 'Произошла ошибка соединения'
    except DBCredentialError as e:
        return 'Не удается войти в бд'
    except DBBaseError as e:
        return 'Произошла непредвиденная ошибка бд'
    except DBSQLError as e:
        return 'Ошибка базы данных'

    session.pop('appointment')

    return redirect('/interview/list')


@interview_blueprint.route('/appointment/clear_candidates', methods=['POST'])
def interview_blueprint_rout_appointment_clear_candidates():
    current_role = get_current_role()

    if current_role != 'admin':
        return redirect('/menu')

    if request.method != 'POST':
        return 'Unknown action'

    if 'appointment' not in session:
        session['appointment'] = {
            'interview_id': None,
            'candidate_ids': []
        }

    appointment = session['appointment']
    interview_id = appointment['interview_id']

    session['appointment'] = {
        'interview_id': interview_id,
        'candidate_ids': []
    }

    return redirect('/interview/appointed')


@interview_blueprint.route('/appointment/remove_candidate', methods=['POST'])
@check_auth
def interview_blueprint_route_appointment_remove_candidate():
    current_role = get_current_role()

    if current_role != 'admin':
        return redirect('/menu')

    if 'appointment' not in session:
        session['appointment'] = {
            'interview_id': None,
            'candidate_ids': []
        }

    appointment = session['appointment']
    candidate_ids = appointment['candidate_ids']

    candidate_id_to_remove = int(request.form.get('candidate_id'))

    if candidate_id_to_remove in candidate_ids:
        candidate_ids.remove(candidate_id_to_remove)

    session['appointment'] = {
        'interview_id': appointment['interview_id'],
        'candidate_ids': candidate_ids
    }

    return redirect('/interview/appointed')


@interview_blueprint.route('/appointment/pick_candidates', methods=['GET', 'POST'])
@check_auth
def interview_blueprint_route_appointment_pick_candidate():
    current_role = get_current_role()

    if current_role != 'admin':
        return redirect('/menu')

    if 'appointment' not in session:
        session['appointment'] = {
            'interview_id': None,
            'candidate_ids': []
        }

    appointment = session['appointment']
    candidate_ids = appointment['candidate_ids']

    if request.method == 'POST':
        new_candidate_id = int(request.form.get('candidate_id'))

        candidate_ids.append(new_candidate_id)

        session['appointment'] = {
            'interview_id': appointment['interview_id'],
            'candidate_ids': candidate_ids
        }

        return redirect('/interview/appointed')
    elif request.method == 'GET':
        try:
            with UseDatabase(current_app.config['db'][current_role]) as cursor:
                if candidate_ids:
                    query_chunk = " where c_id not in (" +\
                                  ','.join(str(id) for id in candidate_ids) +\
                                  ')'
                else:
                    query_chunk = ""

                get_candidates_query = f"""
                select c_id, name, age, gender, address from candidate {query_chunk}
                """

                cursor.execute(get_candidates_query)
                candidates = make_dict_list_from_rows(cursor)

                return render_template('interview_appointment_pick_candidates_admin.html',
                                       candidates=candidates if candidates else None)
        except DBConnectionError as e:
            return 'Произошла ошибка соединения'
        except DBCredentialError as e:
            return 'Не удается войти в бд'
        except DBBaseError as e:
            return 'Произошла непредвиденная ошибка бд'
        except DBSQLError as e:
            return 'Ошибка базы данных'

    else:
        return 'Unknown action'


@interview_blueprint.route('/appointment/pick_interview', methods=['GET', 'POST'])
@check_auth
def interview_blueprint_route_appointment_pick_interview():
    current_role = get_current_role()

    if current_role != 'admin':
        return redirect('/menu')

    if 'appointment' not in session:
        session['appointment'] = {
            'interview_id': None,
            'candidate_ids': []
        }

    if request.method == 'POST':
        session['appointment'] = {
            'interview_id': int(request.form.get('interview_id')),
            'candidate_ids': session['appointment']['candidate_ids']
        }
        return redirect('/interview/appointed')
    elif request.method == 'GET':
        appointment = session['appointment'] \
            if 'appointment' in session \
            else {}

        current_interview_id = appointment['interview_id'] \
            if 'interview_id' in appointment \
            else None

        try:
            with UseDatabase(current_app.config['db'][current_role]) as cursor:
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
                where iv_id not in (select distinct iv_id from interview_result) and iv_id != 4
                order by i.iv_id
                """

                cursor.execute(get_interviews_query)

                interviews = make_dict_list_from_rows(cursor)

                return render_template('interview_appointment_pick_interview_admin.html',
                                       interviews=interviews,
                                       interview_id=current_interview_id)
        except DBConnectionError as e:
            return 'Произошла ошибка соединения'
        except DBCredentialError as e:
            return 'Не удается войти в бд'
        except DBBaseError as e:
            return 'Произошла непредвиденная ошибка бд'
        except DBSQLError as e:
            return 'Ошибка базы данных'
    else:
        return 'Unknown action'
