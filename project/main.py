# main.py

from flask import Blueprint, render_template, request, flash
from flask_login import login_required, current_user
from .models.models import Database_access
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import exc

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
    data_database = Database_access.query.filter_by(
        user_id=current_user.id).first()
    return render_template('database.html', name=current_user.name, data_database=data_database)


@main.route('/database/action/<action>', methods=['POST'])
@login_required
def database_action(action):

    error = ''
    data_database = Database_access.query.filter_by(
        user_id=current_user.id).first()

    if action == 'create':
        try:
            db_user = request.form.get('db_user')
            db_password = request.form.get('db_password')
            db_host = request.form.get('db_host')
            db_name = request.form.get('db_name')

            new_database = Database_access(db_user=db_user, user_id=current_user.id, db_host=db_host,
                                           db_password=db_password, db_name=db_name)
            db.session.add(new_database)
            db.session.commit()

            flash('Banco de dados cadastrado')

        except exc.SQLAlchemyError as error:
            error = str(error.orig) + " for parameters " + \
                str(error.params), 'error'

    if action == 'delete':
        try:
            db_delete = request.form.get('db_delete')
            if db_delete == 'deletar':
                database_access = Database_access.query.filter_by(
                    user_id=current_user.id)
                db.session.delete(database_access)
                db.session.commit()

                flash('Informações de banco de dados excluídas com sucesso!')
            else:
                error = 'Por favor, digite deletar para confirmar a exclusão de informações.'

        except exc.SQLAlchemyError as error:
            error = str(error.orig) + " for parameters " + \
                str(error.params), 'error'

    return render_template('database.html', name=current_user.name, error=error, data_database=data_database)
