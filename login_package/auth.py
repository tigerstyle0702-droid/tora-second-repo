import os
import datetime
import re
from flask import Blueprint, render_template, request, redirect, url_for, flash

bp = Blueprint('auth', __name__, template_folder='.', static_folder='static')

PASSWORD_FILE = 'password.txt'
HISTORY_FILE = 'password_history.txt'


def load_password():
    if os.path.exists(PASSWORD_FILE):
        with open(PASSWORD_FILE, 'r') as f:
            lines = f.readlines()
            if len(lines) >= 2:
                password = lines[0].strip()
                expiry_date = datetime.datetime.strptime(lines[1].strip(), '%Y-%m-%d')
                return password, expiry_date
    expiry_date = datetime.datetime.now() + datetime.timedelta(days=180)
    return '0000000000', expiry_date


def save_password(password, expiry_date):
    with open(PASSWORD_FILE, 'w') as f:
        f.write(password + '\n')
        f.write(expiry_date.strftime('%Y-%m-%d') + '\n')


def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            return [line.strip() for line in f.readlines()]
    return []


def save_history(history):
    with open(HISTORY_FILE, 'w') as f:
        for pwd in history:
            f.write(pwd + '\n')


def is_password_valid(password):
    if len(password) < 8:
        return False
    if not re.match(r'^[a-zA-Z0-9!@#$%^&*()_+\-=[]{};\':"\\|,.<>\/?]*$', password):
        return False
    return True


@bp.route('/')
def login():
    password, expiry_date = load_password()
    now = datetime.datetime.now()
    warning = (expiry_date - now).days <= 7
    return render_template('login.html', warning=warning)


@bp.route('/login', methods=['POST'])
def do_login():
    username = request.form.get('username', '').strip()
    password_input = request.form.get('password', '')

    if not username:
        flash('ユーザー名を入力してください。', 'error')
        return redirect(url_for('auth.login'))
    if len(username) > 20:
        flash('ユーザー名は20文字以内で入力してください。', 'error')
        return redirect(url_for('auth.login'))
    if not password_input:
        flash('パスワードを入力してください。', 'error')
        return redirect(url_for('auth.login'))

    current_password, _ = load_password()
    if password_input != current_password:
        flash('ユーザー名またはパスワードが間違っています。', 'error')
        return redirect(url_for('auth.login'))

    flash('ログイン成功！', 'success')
    return redirect(url_for('auth.login'))


@bp.route('/change_password')
def change_password():
    return render_template('change_password.html')


@bp.route('/update_password', methods=['POST'])
def update_password():
    current_password_input = request.form['current_password']
    new_password = request.form['new_password']
    confirm_password = request.form['confirm_password']

    current_password, expiry_date = load_password()
    history = load_history()

    if current_password_input != current_password:
        flash('現在のパスワードが間違っています。', 'error')
        return redirect(url_for('auth.change_password'))

    if new_password == current_password:
        flash('新しいパスワードは現在のパスワードと同じにできません。', 'error')
        return redirect(url_for('auth.change_password'))

    if new_password in history[-5:]:
        flash('新しいパスワードは過去5回使用したパスワードと同じにできません。', 'error')
        return redirect(url_for('auth.change_password'))

    if new_password != confirm_password:
        flash('新しいパスワードと確認用パスワードが一致しません。', 'error')
        return redirect(url_for('auth.change_password'))

    if not is_password_valid(new_password):
        flash('新しいパスワードは半角英数と記号のみで8文字以上である必要があります。', 'error')
        return redirect(url_for('auth.change_password'))

    history.append(current_password)
    save_history(history[-5:])
    new_expiry = datetime.datetime.now() + datetime.timedelta(days=180)
    save_password(new_password, new_expiry)

    flash('パスワードが変更されました。', 'success')
    return redirect(url_for('auth.login'))
