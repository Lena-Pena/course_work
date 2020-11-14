import json
import os

from flask import Blueprint, redirect, render_template

from auth import has_active_session


def create_menu_blueprint(auth_failed_route):
    menu_blueprint = Blueprint('menu_blueprint', __name__, template_folder='templates')

    @menu_blueprint.route('/', methods=['GET'])
    def menu_blueprint_route_menu():
        if not has_active_session():
            return redirect(auth_failed_route)

        try:
            menu_config = open('menu/menu.config.json', 'r')
            links = json.load(menu_config)

            return render_template('menu.html', links=links)
            # return json.dumps(links)
        except Exception as e:
            return 'Can\'t read menu config.{} Try to reload page!.{}'.format(os.getcwd(), e)

    return menu_blueprint
