from flask import Blueprint, session, redirect, request, render_template, current_app

menu_blueprint = Blueprint('menu_blueprint', __name__, template_folder='templates')


@menu_blueprint.route('/', methods=['GET'])
def menu_blueprint_route_menu():
    return render_template('menu.html')
