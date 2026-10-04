from pathlib import Path
import sys

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'frontend'))
from passwords import hash_password, verify_password


def test_password_hashes_and_legacy_accounts():
    stored = hash_password('test-password')
    assert stored != 'test-password'
    assert verify_password('test-password', stored)
    assert not verify_password('wrong-password', stored)
    assert verify_password('legacy', 'legacy')
    assert not verify_password('test', 'pbkdf2_sha256$bad')


def test_signup_hr_login_and_logout(monkeypatch, tmp_path):
    monkeypatch.setenv('DATA_DIR', str(tmp_path))
    app = AppTest.from_file(str(ROOT / 'frontend/home.py')).run()
    assert not app.exception
    app.sidebar.radio[0].set_value('Sign Up').run()
    app.text_input[0].set_value('test_hr')
    app.text_input[1].set_value('test-password')
    app.selectbox[0].set_value('HR')
    app.button[0].click().run()
    assert app.success
    assert 'test-password' not in (tmp_path / 'users.json').read_text()
    app.sidebar.radio[0].set_value('Login').run()
    app.sidebar.text_input[0].set_value('test_hr')
    app.sidebar.text_input[1].set_value('wrong-password')
    app.sidebar.button[0].click().run()
    assert app.error[0].value == 'Invalid username or password.'
    app.sidebar.text_input[1].set_value('test-password')
    app.sidebar.button[0].click().run()
    assert any('HR Dashboard' in title.value for title in app.title)
    assert app.session_state['role'] == 'HR'
    app.session_state['hr_result'] = {'answer': 'cached answer', 'sources': []}
    app.sidebar.button[0].click().run()
    assert app.session_state['logged_in'] is False
    assert 'hr_result' not in app.session_state
    assert not app.exception
