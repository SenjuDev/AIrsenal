#!/usr/bin/env python

"""
API for calling airsenal functions.
HTTP requests to the endpoints defined here will give rise
to calls to functions in api_utils.py
"""

import os
import sys
from flask import Blueprint, Flask, Response, session, request, jsonify
from flask_cors import CORS
from flask_session import Session
import requests
import json
from uuid import uuid4
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

from airsenal.framework.utils import CURRENT_SEASON, list_players, get_last_finished_gameweek, fetcher
from airsenal.framework.api_utils import *
from airsenal.framework.schema import SessionTeam, engine

from exceptions import ApiException


def get_session_id():
    """
    Get the ID from the flask_session Session instance if
    it exists, otherwise just get a default string, which
    will enable us to test some functionality just via python requests.
    """
    if "key" in session.keys():
        return session["key"]
    else:
        return "DEFAULT_SESSION_ID"


## Use a flask blueprint rather than creating the app directly
## so that we can also make a test app

blueprint = Blueprint("airsenal",__name__)

@blueprint.errorhandler(ApiException)
def handle_exception(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

@blueprint.teardown_request
def remove_session(ex=None):
    remove_db_session()


@blueprint.route("/players/<team>/<pos>", methods=["GET"])
def get_player_list(team, pos):
    """
    return a list of all players in that team and/or position
    """
    return create_response(list_players_teams_prices(position=pos,
                                                     team=team))


@blueprint.route("/new")
def set_session_key():
    """
    Create a new and unique session ID
    """
    key = str(uuid4())
    session['key'] = key
    return create_response(key)


@blueprint.route("/team/new")
def reset_team():
    """
    Remove all players from the DB table with this session_id and
    reset the budget to 100M
    """
    reset_session_team(get_session_id())
    return create_response("OK")


@blueprint.route("/team/add/<player_id>")
def add_player(player_id):
    added_ok = add_session_player(player_id, session_id=get_session_id())
    return create_response(added_ok)


@blueprint.route("/team/remove/<player_id>")
def remove_player(player_id):
    removed_ok = remove_session_player(player_id, session_id=get_session_id())
    return create_response(removed_ok)


@blueprint.route("/team/list",methods=["GET"])
def list_session_players():
    player_list = get_session_players(session_id=get_session_id())
    return create_response(player_list)

@blueprint.route("/team/pred",methods=["GET"])
def list_session_predictions():
    pred_dict = get_session_predictions(session_id=get_session_id())
    return create_response(pred_dict)


@blueprint.route("/team/validate",methods=["GET"])
def validate_session_players():
    valid = validate_session_squad(session_id=get_session_id())
    return create_response(valid)


@blueprint.route("/team/fill/<team_id>")
def fill_team_from_team_id(team_id):
    player_ids = fill_session_team(team_id=team_id,session_id=get_session_id())
    return create_response(player_ids)


@blueprint.route("/budget", methods=["GET","POST"])
def session_budget():
    if request.method == 'POST':
        data = json.loads(request.data.decode("utf-8"))
        budget = data["budget"]
        set_session_budget(budget, get_session_id())
        return create_response("OK")
    else:
        return create_response(get_session_budget(get_session_id()))


###########################################

def create_app(name = __name__):
    app = Flask(name)
    app.config['SESSION_TYPE'] = 'filesystem'
    app.secret_key = 'blah'
    CORS(app, supports_credentials=True)
    app.register_blueprint(blueprint)
    Session(app)
    return app


if __name__ == "__main__":

    app = create_app()
    app.run(host='0.0.0.0',port=5002, debug=True)