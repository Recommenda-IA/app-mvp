# main.py

from flask import Blueprint, render_template, request, flash
from flask_paginate import Pagination, get_page_parameter
from flask_login import login_required, current_user
from .models.models import Database_access, Training_frequency, Transactions
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import exc, create_engine

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('pages/index.html')


@main.route('/price')
def price():
    return render_template('pages/index.html')


@main.route('/products')
def products():
    return render_template('pages/index.html')


@main.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard/dashboard.html', name=current_user.name)


@main.route('/profile')
@login_required
def profile():
    return render_template('dashboard/profile.html', name=current_user.name)


@main.route('/database')
@login_required
def database():
    error = ''
    error_db_user = ''
    data_database = Database_access.query.filter_by(
        user_id=current_user.id).first()
    database_user_conected = False

    if data_database:
        usuario_db = data_database.db_user
        senha_db = data_database.db_password
        host_db = data_database.db_host
        database = data_database.db_name

        if data_database.db_sgbd == 'mysql':
            engine = create_engine(
                f"mysql+mysqlconnector://{usuario_db}:{senha_db}@{host_db}/{database}", connect_args={'connect_timeout': 5})

        if data_database.db_sgbd == 'postgresql':
            engine = create_engine(
                f"postgresql+psycopg2://{usuario_db}:{senha_db}@{host_db}/{database}", connect_args={'connect_timeout': 5})

        try:
            conn = engine.connect()
            database_user_conected = True
        except exc.SQLAlchemyError as query_error:
            error_db_user = str(query_error.orig) + " for parameters " + \
                str(query_error.params)

    return render_template('dashboard/database.html', name=current_user.name, data_database=data_database, error=error, error_db_user=error_db_user, database_user_conected=database_user_conected)


@main.route('/database/<action>', methods=['POST'])
@login_required
def database_action(action):
    error = ''
    error_db_user = ''
    data_database = Database_access.query.filter_by(
        user_id=current_user.id).first()
    database_user_conected = False

    if data_database:
        usuario_db = data_database.db_user
        senha_db = data_database.db_password
        host_db = data_database.db_host
        database = data_database.db_name

        if data_database.db_sgbd == 'mysql':
            engine = create_engine(
                f"mysql+mysqlconnector://{usuario_db}:{senha_db}@{host_db}/{database}", connect_args={'connect_timeout': 5})

        if data_database.db_sgbd == 'postgresql':
            engine = create_engine(
                f"postgresql+psycopg2://{usuario_db}:{senha_db}@{host_db}/{database}", connect_args={'connect_timeout': 5})

        try:
            conn = engine.connect()
            database_user_conected = True
        except exc.SQLAlchemyError as query_error:
            error_db_user = str(query_error.orig) + " for parameters " + \
                str(query_error.params)

    if action == 'create':
        try:
            db_user = request.form.get('db_user')
            db_password = request.form.get('db_password')
            db_host = request.form.get('db_host')
            db_name = request.form.get('db_name')
            db_sgbd = request.form.get('db_sgbd')
            db_view = request.form.get('db_view')

            new_database = Database_access(db_user=db_user, user_id=current_user.id, db_host=db_host,
                                           db_password=db_password, db_name=db_name, db_view=db_view, db_sgbd=db_sgbd)
            db.session.add(new_database)
            db.session.commit()

            flash('Banco de dados cadastrado com sucesso.', 'success')

            error = ''
            data_database = Database_access.query.filter_by(
                user_id=current_user.id).first()
            database_user_conected = True

        except exc.SQLAlchemyError as error_query:
            error = str(error_query.orig) + " for parameters " + \
                str(error_query.params), 'error'

    if action == 'delete':
        try:
            db_delete = request.form.get('db_delete')
            if db_delete == 'deletar banco de dados':
                Database_access.query.filter_by(
                    user_id=current_user.id).delete()
                db.session.commit()

                flash('Informações de banco de dados excluídas com sucesso.', 'success')

                error = ''
                data_database = Database_access.query.filter_by(
                    user_id=current_user.id).first()
            else:
                error = 'Por favor, digite "deletar banco de dados" para confirmar a exclusão de informações.'

        except exc.SQLAlchemyError as error_query:
            error = str(error_query.orig) + " for parameters " + \
                str(error_query.params), 'error'

    return render_template('dashboard/database.html', name=current_user.name, error=error, data_database=data_database, database_user_conected=database_user_conected, error_db_user=error_db_user)


@main.route('/training-settings')
@login_required
def training():
    error = ''
    data_training = Training_frequency.query.filter_by(
        user_id=current_user.id).first()

    return render_template('dashboard/training-settings.html', name=current_user.name, error=error, data_training=data_training)


@main.route('/training-settings/<action>', methods=['POST'])
@login_required
def training_action(action):
    error = ''
    data_training = Training_frequency.query.filter_by(
        user_id=current_user.id).first()

    if action == 'create':
        try:
            tr_frequency = request.form.get('tr_frequency')
            tr_activated = request.form.get('tr_activated')

            new_training = Training_frequency(
                tr_frequency=tr_frequency, user_id=current_user.id, tr_activated=tr_activated)
            db.session.add(new_training)
            db.session.commit()

            flash('Configurações salvas com sucesso.', 'success')

            error = ''
            data_training = Training_frequency.query.filter_by(
                user_id=current_user.id).first()

        except exc.SQLAlchemyError as error_query:
            error = str(error_query.orig) + " for parameters " + \
                str(error_query.params), 'error'

    if action == 'update':
        try:
            data_training.tr_frequency = request.form.get('tr_frequency')
            data_training.tr_activated = request.form.get('tr_activated')

            db.session.commit()

            flash('Configurações atualizadas com sucesso.', 'success')

            error = ''
            """ data_training = Training_frequency.query.filter_by(
                    user_id=current_user.id).first() """

        except exc.SQLAlchemyError as error_query:
            error = str(error_query.orig) + " for parameters " + \
                str(error_query.params), 'error'

    return render_template('dashboard/training-settings.html', name=current_user.name, error=error, data_training=data_training)


@main.route('/upload')
@login_required
def upload():
    error = ''

    return render_template('dashboard/upload.html', name=current_user.name, error=error, data_training='')


@main.route('/upload/create', methods=['POST'])
@login_required
def upload_create():
    error = ''
    arquivo = request.files['arquivo']

    if arquivo.filename.endswith('.csv'):
        # Processar arquivo CSV
        linhas = arquivo.stream.read().decode('utf-8').splitlines()
        rotulos = linhas[0].split(',')
        dados = [linha.split(',') for linha in linhas[1:]]
    else:
        # Processar arquivo Excel
        # Requer a biblioteca pandas e openpyxl
        import pandas as pd
        df = pd.read_excel(arquivo)
        rotulos = df.columns.tolist()
        dados = df.values.tolist()

    if 'id_transaction' not in rotulos:
        error = 'Sem rótulo id_produto'
        return render_template('dashboard/upload.html', name=current_user.name, error=error)

    if 'id_item' not in rotulos:
        error = 'Sem rótulo id_item'
        return render_template('dashboard/upload.html', name=current_user.name, error=error)

    if 'name_item' not in rotulos:
        error = 'Sem rótulo name_item'
        return render_template('dashboard/upload.html', name=current_user.name, error=error)

    if 'customer_id' not in rotulos:
        error = 'Sem rótulo customer_id'
        return render_template('dashboard/upload.html', name=current_user.name, error=error)

    if 'data_transaction' not in rotulos:
        error = 'Sem rótulo data_transaction'
        return render_template('dashboard/upload.html', name=current_user.name, error=error)

    for linha in dados:
        if len(linha) != 5:
            error = 'Dados incorretos. Verifique se os dados do arquivo seguem o padrão necessário ou se existem vírgulas entre os valores do arquivo.'
            return render_template('dashboard/upload.html', name=current_user.name, error=error)

        id_transaction, id_item, name_item, customer_id, data_transaction = linha
        transaction = Transactions(
            id_transaction=id_transaction,
            id_item=id_item,
            name_item=name_item,
            customer_id=customer_id,
            data_transaction=data_transaction,
            user_id=current_user.id
        )
        try:
            db.session.add(transaction)
            db.session.commit()
        except exc.SQLAlchemyError as error_query:
            error = str(error_query.orig) + " for parameters " + \
                str(error_query.params), 'error'

    flash('Dados salvos com sucesso!')
    return render_template('dashboard/upload.html', name=current_user.name, error=error)


@main.route('/view-data')
@login_required
def view_data():
    error = ''

    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 25

    pagination = Transactions.query.order_by(Transactions.created_at.desc()).paginate(
        page=page, per_page=per_page)
    transactions = pagination.items
    pagination_range = pagination.iter_pages(
        left_edge=2,
        left_current=2,
        right_current=3,
        right_edge=2
    )

    return render_template('dashboard/view-data.html', name=current_user.name, error=error, transactions=transactions, pagination=pagination, pagination_range=pagination_range)


@main.route('/data-management')
def data_management():
    error = ''

    return render_template('dashboard/data-management.html', name=current_user.name)


@main.route('/data-management/delete', methods=['POST'])
def data_management_delete():
    error = ''

    try:
        db_delete = request.form.get('db_delete')
        if db_delete == 'deletar informações':
            Transactions.query.filter_by(
                user_id=current_user.id).delete()
            db.session.commit()

            flash('Informações de transações excluídas com sucesso.', 'success')

            error = ''
        else:
            error = 'Por favor, digite "deletar informações" para confirmar a exclusão de informações.'

    except exc.SQLAlchemyError as error_query:
        error = str(error_query.orig) + " for parameters " + \
            str(error_query.params), 'error'

    return render_template('dashboard/data-management.html', name=current_user.name, error=error)
