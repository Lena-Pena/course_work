import json
import os

from flask import Blueprint, render_template

from auth import check_auth

menu_blueprint = Blueprint('menu_blueprint', __name__, template_folder='templates')


@menu_blueprint.route('/', methods=['GET'])
@check_auth
def menu_blueprint_route_menu():
    try:
        menu_config = open('data_files/menu.config.json', 'r')
        links = json.load(menu_config)

        return render_template('menu.html', links=links)
        # return json.dumps(links)
    except Exception as e:
        return 'Can\'t read menu config.{} Try to reload page!.{}'.format(os.getcwd(), e)
