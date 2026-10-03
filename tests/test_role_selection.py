from pathlib import Path
import sys

from streamlit.testing.v1 import AppTest

FRONTEND = Path(__file__).resolve().parents[1] / 'frontend'


def screen(role='Employee'):
    app = AppTest.from_string(f'''
import sys
sys.path.insert(0, {str(FRONTEND)!r})
import streamlit as st
from role_selection import choose_role
role = choose_role({role!r})
st.success('Opened ' + role + ' workspace')
''')
    return app.run()


def test_signin_requires_explicit_role_selection():
    app = screen()
    assert app.radio[0].value is None
    assert not app.success
    app.button[0].click().run()
    assert app.warning[0].value == 'Select a role to continue.'
    assert not app.success


def test_employee_selection_opens_workspace():
    app = screen()
    app.radio[0].set_value('Employee')
    app.button[0].click().run()
    assert app.success[0].value == 'Opened Employee workspace'
    assert not app.exception


def test_role_choice_cannot_elevate_employee_account():
    for role in ('HR', 'IT', 'Admin'):
        app = screen()
        app.radio[0].set_value(role)
        app.button[0].click().run()
        assert 'Your account has Employee access' in app.warning[0].value
        assert not app.success
        assert 'signin_role' not in app.session_state


def test_assigned_hr_can_open_hr_or_employee_and_change_workspace():
    app = screen('HR')
    app.radio[0].set_value('HR')
    app.button[0].click().run()
    assert app.success[0].value == 'Opened HR workspace'
    app.sidebar.button[0].click().run()
    assert app.radio[0].value is None
    app.radio[0].set_value('Employee')
    app.button[0].click().run()
    assert app.success[0].value == 'Opened Employee workspace'
