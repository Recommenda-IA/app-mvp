# main.py

from flask import Blueprint, render_template, request, flash
from flask_login import login_required, current_user
from .models.models import Database_access
from . import db
from werkzeug.security import generate_password_hash, check_password_hash

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/price')
def price():
    return render_template('index.html')


@main.route('/products')
def products():
    return render_template('index.html')


@main.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', name=current_user.name)


@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name)


@main.route('/database')
@login_required
def database():
    return render_template('database.html', name=current_user.name)


@main.route('/database/save-database', methods=['POST'])
@login_required
def database_save():
    db_user = request.form.get('db_user')
    db_password = request.form.get('db_password')
    db_host = request.form.get('db_host')
    db_name = request.form.get('db_name')

    new_database = Database_access(db_user=db_user, db_host=db_host,
                                   db_password=generate_password_hash(db_password, method='sha256'), db_name=db_name)
    db.session.add(new_database)
    db.session.commit()

    flash('Banco de dados cadastrado')

    return render_template('database.html', name=current_user.name)
