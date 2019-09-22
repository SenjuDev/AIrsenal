"""
test that functions supporting our API work.
"""

import pytest
import requests
import re

from ..framework.api_utils import *
from .fixtures import test_session_scope, fill_players, API_SESSION_ID


def test_reset_session_team():
    with test_session_scope() as ts:
        assert(reset_session_team(session_id=API_SESSION_ID, dbsession=ts))
        st = ts.query(SessionTeam).filter_by(session_id=API_SESSION_ID).all()
        assert(len(st)==0)
        sb = ts.query(SessionBudget).filter_by(session_id=API_SESSION_ID).all()
        assert(len(sb)==1)
        assert(sb[0].budget==1000)
        assert(get_session_budget(API_SESSION_ID)==1000)


def test_list_all_players():
    with test_session_scope() as ts:
        fill_players()
        player_list = list_players_teams_prices(dbsession=DBSESSION)
        assert(isinstance(player_list, list))
        assert(len(player_list) > 0)
        first_player = player_list[0]
        # test the format of the returned strings
        assert(re.search("[\w\s]+\([A-Z]{3}\)\: [\d\.]+",first_player))


def test_add_player():
    with test_session_scope() as ts:
        assert(reset_session_team(session_id=API_SESSION_ID, dbsession=ts))
        assert(add_session_player(123, API_SESSION_ID, ts))
        players = get_session_players(API_SESSION_ID, ts)
        assert(len(players)==1)
        assert(players[0]==123)


def test_cant_add_same_player_twice():
    with test_session_scope() as ts:
        assert(reset_session_team(session_id=API_SESSION_ID, dbsession=ts))
        assert(add_session_player(123, API_SESSION_ID, ts))
        assert(not add_session_player(123, API_SESSION_ID, ts))
        players = get_session_players(API_SESSION_ID, ts)
        assert(len(players)==1)
        assert(players[0]==123)


def test_remove_player():
    with test_session_scope() as ts:
        assert(reset_session_team(session_id=API_SESSION_ID, dbsession=ts))
        assert(add_session_player(123, API_SESSION_ID, ts))
        assert(remove_session_player(123, API_SESSION_ID, ts))
        players = get_session_players(API_SESSION_ID, ts)
        assert(len(players)==0)


def test_get_budget():
    with test_session_scope() as ts:
        assert(reset_session_team(session_id=API_SESSION_ID, dbsession=ts))
        assert(get_session_budget(API_SESSION_ID, ts)==1000)


def test_set__get_budget():
    with test_session_scope() as ts:
        assert(reset_session_team(session_id=API_SESSION_ID, dbsession=ts))
        assert(set_session_budget(500, API_SESSION_ID, ts))
        assert(get_session_budget(API_SESSION_ID, ts)==500)