# main.py

from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_paginate import Pagination, get_page_parameter
from flask_login import login_required, current_user
from sqlalchemy import exc, create_engine, inspect, text
from hashlib import md5
from datetime import datetime
import pytz
import pandas as pd
from .helpers.freq_rules import create_association_rules
from .models.models import Database_access, Training_frequency, Transactions, User_api, Training_status, Items, User
from .models.mongo_model import Mongo
from . import db
from werkzeug.security import generate_password_hash

main = Blueprint('main', __name__)


@main.route('/')
def index():
    if current_user.is_authenticated:
        return render_template('dashboard/dashboard.html', name=current_user.name)
    return render_template('pages/login.html')


@main.route('/price')
def price():
    return render_template('pages/login.html')


@main.route('/products')
def products():
    return render_template('pages/login.html')


@main.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard/dashboard.html', name=current_user.name)


@main.route('/profile')
@login_required
def profile():
    return render_template('dashboard/profile.html', user=current_user)

@main.route('/profile/<action>', methods=['POST'])
@login_required
def profile_action(action):

    if action == 'update':
        try:
            email = request.form.get('email')
            password = request.form.get('password')
            password2 = request.form.get('password2')
            name = request.form.get('name')

            if name == '' or email == '':
                flash('Nome e e-mail são obrigatórios.', 'error')
                return redirect(url_for('main.profile'))
            
            if password != '' and password2 != '':
                if password != password2 != '':
                    flash('As senhas não correspondem.', 'error')
                    return redirect(url_for('main.profile'))

            db_user = User.query.filter_by(
                id=current_user.id).first()

            db_user.name = name
            db_user.email = email

            if password != '':
                db_user.password = generate_password_hash(password, method='sha256')

            db.session.commit()

            flash('Usuário atualizado com sucesso.', 'success')
            return redirect(url_for('main.profile'))

        except exc.SQLAlchemyError as error_query:
            flash(str(error_query.orig.args) + " for parameters " +
                  str(error_query.params), 'error')


    return render_template('dashboard/profile.html', user=current_user)


@main.route('/database')
@login_required
def database():
    error_db_user = ''
    data_database = Database_access.query.filter_by(
        user_id=current_user.id).first()
    database_user_conected = False
    transactions_from_database = ''
    date_interval = ''

    if data_database:
        usuario_db = data_database.db_user
        senha_db = data_database.db_password
        host_db = data_database.db_host
        port_db = data_database.db_port
        database = data_database.db_name
        view_db = data_database.db_view

        if data_database.db_sgbd == 'mysql':
            engine = create_engine(
                f"mysql+mysqlconnector://{usuario_db}:{senha_db}@{host_db}:{port_db}/{database}", connect_args={'connect_timeout': 5})

        if data_database.db_sgbd == 'postgresql':
            engine = create_engine(
                f"postgresql+psycopg2://{usuario_db}:{senha_db}@{host_db}:{port_db}/{database}", connect_args={'connect_timeout': 5})

        try:
            conn = engine.connect()
            database_user_conected = True

            inspector = inspect(engine)
            view_name = view_db
            required_columns = ['id_transaction', 'id_item',
                                'name_item', 'customer_id', 'data_transaction']

            if view_name in inspector.get_view_names():
                view_columns = [column['name']
                                for column in inspector.get_columns(view_name)]

                if not all(column in view_columns for column in required_columns):
                    # Algumas colunas estão faltando na view "transacoes"
                    missing_columns = set(required_columns) - set(view_columns)
                    error_message = f"As seguintes colunas obrigatórias estão faltando na view '{view_name}': {', '.join(missing_columns)}"
                    flash(error_message, 'error')
                else:
                    query = text(
                        f"SELECT * FROM {view_name} ORDER BY data_transaction DESC LIMIT 5;")
                    transactions_from_database = conn.execute(query)

                    query_date = text(
                        f"SELECT MAX(data_transaction) as max_date,  MIN(data_transaction) as min_date FROM {view_name};")
                    date_interval = conn.execute(query_date)
            else:
                # A view "transacoes" não existe
                error_message = f"A view '{view_name}' não existe no banco de dados cadastrado."
                flash(error_message, 'error')

            engine.dispose()

        except exc.SQLAlchemyError as query_error:
            error_db_user = str(query_error.orig.args) + \
                " for parameters " + str(query_error.params)

    return render_template('dashboard/database.html', name=current_user.name, data_database=data_database, error_db_user=error_db_user, database_user_conected=database_user_conected, transactions_from_database=transactions_from_database, date_interval=date_interval)


@main.route('/database/<action>', methods=['POST'])
@login_required
def database_action(action):

    if action == 'create':
        try:
            db_user = request.form.get('db_user')
            db_password = request.form.get('db_password')
            db_host = request.form.get('db_host')
            db_name = request.form.get('db_name')
            db_sgbd = request.form.get('db_sgbd')
            db_view = request.form.get('db_view')
            db_port = request.form.get('db_port')

            if db_user == '' or db_password == '' or db_host == '' or db_name == '' or db_sgbd == '' or db_view == '' or db_port == '':
                flash('Todas as informações são obrigatórias.', 'error')
                return redirect(url_for('main.database'))

            new_database = Database_access(db_user=db_user, user_id=current_user.id, db_host=db_host,
                                           db_password=db_password, db_name=db_name, db_view=db_view, db_sgbd=db_sgbd, db_port=db_port)
            db.session.add(new_database)
            db.session.commit()

            flash('Banco de dados cadastrado com sucesso.', 'success')

        except exc.SQLAlchemyError as error_query:
            flash(str(error_query.orig.args) + " for parameters " +
                  str(error_query.params), 'error')

    if action == 'update':
        try:
            db_user = request.form.get('db_user')
            db_password = request.form.get('db_password')
            db_host = request.form.get('db_host')
            db_name = request.form.get('db_name')
            db_sgbd = request.form.get('db_sgbd')
            db_view = request.form.get('db_view')
            db_port = request.form.get('db_port')

            if db_user == '' or db_password == '' or db_host == '' or db_name == '' or db_sgbd == '' or db_view == '' or db_port == '':
                flash('Todas as informações são obrigatórias.', 'error')
                return redirect(url_for('main.database'))

            database = Database_access.query.filter_by(
                user_id=current_user.id).first()

            database.db_user = db_user
            database.db_password = db_password
            database.db_host = db_host
            database.db_name = db_name
            database.db_sgbd = db_sgbd
            database.db_view = db_view
            database.db_port = db_port

            db.session.commit()

            flash('Banco de dados atualizado com sucesso.', 'success')

        except exc.SQLAlchemyError as error_query:
            flash(str(error_query.orig.args) + " for parameters " +
                  str(error_query.params), 'error')

    if action == 'delete':
        try:
            db_delete = request.form.get('db_delete')
            if db_delete == 'deletar banco de dados':
                Database_access.query.filter_by(
                    user_id=current_user.id).delete()
                db.session.commit()

                flash('Informações de banco de dados excluídas com sucesso.', 'success')
            else:
                flash(
                    'Por favor, digite "deletar banco de dados" para confirmar a exclusão de informações.', 'error')

        except exc.SQLAlchemyError as error_query:
            flash(str(error_query.orig.args) + " for parameters " +
                  str(error_query.params), 'error')

    return redirect(url_for('main.database'))


@main.route('/training-settings')
@login_required
def training():
    data_training = Training_frequency.query.filter_by(
        user_id=current_user.id).first()

    return render_template('dashboard/training-settings.html', name=current_user.name, data_training=data_training)


@main.route('/training-settings/<action>', methods=['POST'])
@login_required
def training_action(action):

    if action == 'create':
        try:
            tr_frequency = request.form.get('tr_frequency')
            tr_activated = request.form.get('tr_activated')

            new_training = Training_frequency(
                tr_frequency=tr_frequency, user_id=current_user.id, tr_activated=tr_activated)
            db.session.add(new_training)
            db.session.commit()

            flash('Configurações salvas com sucesso.', 'success')

        except exc.SQLAlchemyError as error_query:
            flash(str(error_query.orig.args) + " for parameters " +
                  str(error_query.params), 'error')

    if action == 'update':
        try:
            data_training = Training_frequency.query.filter_by(
                user_id=current_user.id).first()
            data_training.tr_frequency = request.form.get('tr_frequency')
            data_training.tr_activated = request.form.get('tr_activated')

            db.session.commit()

            flash('Configurações atualizadas com sucesso.', 'success')

        except exc.SQLAlchemyError as error_query:
            flash(str(error_query.orig.args) + " for parameters " +
                  str(error_query.params), 'error')

    return redirect(url_for('main.training'))


@main.route('/upload')
@login_required
def upload():
    return render_template('dashboard/upload.html', name=current_user.name)


@main.route('/upload/create', methods=['POST'])
@login_required
def upload_create():
    arquivo = request.files['arquivo']

    if arquivo.filename.endswith('.csv'):
        # Processar arquivo CSV
        linhas = arquivo.stream.read().decode('utf-8').splitlines()
        rotulos = linhas[0].split(',')
        dados = [linha.split(',') for linha in linhas[1:]]
    elif arquivo.filename.endswith('.xlsx') or arquivo.filename.endswith('.xls'):
        # Processar arquivo Excel
        try:
            df = pd.read_excel(arquivo)
            rotulos = df.columns.tolist()
            dados = df.values.tolist()
        except Exception as e:
            flash('Erro ao processar o arquivo Excel: ' + str(e), 'error')
            return redirect(url_for('main.upload'))
    else:
        flash('Formato de arquivo inválido. O arquivo deve ser CSV ou Excel.', 'error')
        return redirect(url_for('main.upload'))

    # Verifica se existem os labels requeridos
    required_labels = ['id_transaction', 'id_item',
                       'name_item', 'customer_id', 'data_transaction']
    for label in required_labels:
        if label not in rotulos:
            flash('Sem rótulo ' + label, 'error')
            return redirect(url_for('main.upload'))

    item_data = {}  # Dicionário para armazenar os dados dos itens distintos

    for linha in dados:
        # Verifica se as linhas contem mais do que os itens requeridos
        if len(linha) != 5:
            flash('Dados incorretos. Verifique se os dados do arquivo seguem o padrão necessário ou se existem vírgulas entre os valores do arquivo.', 'error')
            return redirect(url_for('main.upload'))

        id_transaction, id_item, name_item, customer_id, data_transaction = linha

        # Adicionar os dados dos itens distintos ao dicionário
        if id_item not in item_data:
            item_data[id_item] = {
                'id_item': id_item,
                'customer_id': customer_id,
                'user_id': current_user.id,
                'name_item': name_item,
                'created_at': datetime.now()
            }

    batch_size = 1000  # Tamanho do lote
    total_records = len(dados)
    # Calcula o número de lotes
    num_batches = (total_records + batch_size - 1) // batch_size

    for batch_index in range(num_batches):
        start_index = batch_index * batch_size
        end_index = min((batch_index + 1) * batch_size, total_records)
        batch_data = dados[start_index:end_index]

        transactions = []
        for linha in batch_data:
            id_transaction, id_item, name_item, customer_id, data_transaction = linha

            # Utilizar os dados do dicionário para criar os objetos Transactions
            transaction = Transactions(
                id_transaction=id_transaction,
                id_item=id_item,
                name_item=name_item,
                customer_id=customer_id,
                data_transaction=data_transaction,
                user_id=current_user.id,
                created_at=datetime.now()
            )
            transactions.append(transaction)

        try:
            db.session.add_all(transactions)
            db.session.commit()
        except exc.SQLAlchemyError as error_query:
            flash(str(error_query.orig.args) + " for parameters " +
                  str(error_query.params), 'error')

    # Salvar os dados dos itens distintos na tabela "Items"
    item_objects = [Items(**data) for data in item_data.values()]
    try:
        db.session.add_all(item_objects)
        db.session.commit()
    except exc.SQLAlchemyError as error_query:
        flash(str(error_query.orig.args) + " for parameters " +
              str(error_query.params), 'error')

    flash('Dados importados com sucesso!', 'success')
    return redirect(url_for('main.upload'))


@main.route('/status-training')
@login_required
def status_training():
    total_training = Training_status.query.filter_by(
        user_id=current_user.id).count()

    if total_training == 0:
        message = 'Sem treinamentos.'
        return render_template('dashboard/view-training.html', name=current_user.name, message=message)
    else:
        page = request.args.get(get_page_parameter(), type=int, default=1)
        per_page = 30

        pagination = Training_status.query.order_by(Training_status.start.desc()).paginate(
            page=page, per_page=per_page)
        trainings = pagination.items
        pagination_range = pagination.iter_pages(
            left_edge=2,
            left_current=2,
            right_current=3,
            right_edge=2
        )

        # Converter o campo data_created de UTC para America/Sao_Paulo
        for training in trainings:
            training.start = training.start
            training.end = training.end

        return render_template('dashboard/view-training.html', name=current_user.name, trainings=trainings, pagination=pagination, pagination_range=pagination_range, total_training=total_training)


@main.route('/view-transactions')
@login_required
def view_transactions():
    total_transactions = Transactions.query.filter_by(
        user_id=current_user.id).count()

    if total_transactions == 0:
        message = 'Sem registros.'
        return render_template('dashboard/view-transactions.html', name=current_user.name, message=message)
    else:
        page = request.args.get(get_page_parameter(), type=int, default=1)
        per_page = 200

        pagination = Transactions.query.order_by(Transactions.created_at.desc()).paginate(
            page=page, per_page=per_page)
        transactions = pagination.items
        pagination_range = pagination.iter_pages(
            left_edge=2,
            left_current=2,
            right_current=3,
            right_edge=2
        )

        # Converter o campo data_created de UTC para America/Sao_Paulo
        for transaction in transactions:
            transaction.created_at = transaction.created_at

        return render_template('dashboard/view-transactions.html', name=current_user.name, transactions=transactions, pagination=pagination, pagination_range=pagination_range, total_transactions=total_transactions)


@main.route('/view-items')
@login_required
def view_items():
    total_items = Items.query.filter_by(
        user_id=current_user.id).count()

    if total_items == 0:
        message = 'Sem registros.'
        return render_template('dashboard/view-items.html', name=current_user.name, message=message)
    else:
        page = request.args.get(get_page_parameter(), type=int, default=1)
        per_page = 200

        pagination = Items.query.order_by(Items.created_at.desc()).paginate(
            page=page, per_page=per_page)
        items = pagination.items
        pagination_range = pagination.iter_pages(
            left_edge=2,
            left_current=2,
            right_current=3,
            right_edge=2
        )

        # Converter o campo data_created de UTC para America/Sao_Paulo
        for item in items:
            item.created_at = item.created_at

        return render_template('dashboard/view-items.html', name=current_user.name, items=items, pagination=pagination, pagination_range=pagination_range, total_items=total_items)


@main.route('/data-management')
@login_required
def data_management():
    total_transactions = Transactions.query.filter_by(
        user_id=current_user.id).count()
    total_items = Items.query.filter_by(
        user_id=current_user.id).count()

    return render_template('dashboard/data-management.html', name=current_user.name, total_transactions=total_transactions, total_items=total_items)


@main.route('/data-management/delete', methods=['POST'])
@login_required
def data_management_delete():
    try:
        db_delete = request.form.get('db_delete')
        if db_delete == 'deletar dados':
            Transactions.query.filter_by(
                user_id=current_user.id).delete()
            db.session.commit()

            Items.query.filter_by(
                user_id=current_user.id).delete()
            db.session.commit()

            flash('Informações de transações excluídas com sucesso.', 'success')
        else:
            flash(
                'Por favor, digite "deletar informações" para confirmar a exclusão de informações.', 'error')

    except exc.SQLAlchemyError as error_query:
        flash(str(error_query.orig.args) + " for parameters " +
              str(error_query.params), 'error')

    return redirect(url_for('main.data_management'))


@main.route('/api-users')
@login_required
def api_users():

    if User_api.query.filter_by(user_id=current_user.id).count() == 0:
        message = 'Sem registros para usuários API.'
        return render_template('dashboard/api-users.html', name=current_user.name, message=message)
    else:
        data_users = User_api.query.filter_by(user_id=current_user.id)

        # Converter o campo data_created de UTC para America/Sao_Paulo
        for user in data_users:
            user.created_at = user.created_at

        return render_template('dashboard/api-users.html', name=current_user.name, data_users=data_users)

@main.route('/api-docs')
@login_required
def api_docs():

    return render_template('dashboard/api-docs.html')


@main.route('/api-users/<action>', methods=['POST'])
@login_required
def api_users_actions(action):

    if action == 'create':
        try:
            name = request.form.get('api_user')
            user_id = current_user.id

            if User_api.query.filter_by(user_id=user_id).count() >= 5:
                flash('Limite de registros atingido para esta conta.', 'error')
            else:
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                hash_value = 'sk-' + md5(current_time.encode()).hexdigest()

                user = User_api(username=name, hash=hash_value,
                                user_id=user_id)
                db.session.add(user)
                db.session.commit()

                flash('Usuário de API criado com sucesso.', 'success')

        except exc.SQLAlchemyError as error_query:
            flash(str(error_query.orig.args) + " for parameters " +
                  str(error_query.params), 'error')

    if action == 'delete':
        try:
            users_delete = request.form.get('users_delete')
            if users_delete == 'deletar usuário':
                name = request.form.get('api_user')
                user_id = current_user.id

                user_ids = request.form.getlist('api_user[]')
                for user_id in user_ids:
                    user = User_api.query.get(user_id)
                    if user:
                        db.session.delete(user)

                db.session.commit()

                flash('Usuário(s) excluído(s) com sucesso.', 'success')
            else:
                flash(
                    'Por favor, digite "deletar usuário" para confirmar a exclusão de usuários.', 'error')

        except exc.SQLAlchemyError as error_query:
            flash(str(error_query.orig.args) + " for parameters " +
                  str(error_query.params), 'error')

    return redirect(url_for('main.api_users'))


@main.route('/association-rules', methods=['POST'])
def run_association_rules():

    start_training = datetime.now()

    user_id = 1
    start_date = '2000-06-30'
    end_date = '2010-07-02'

    print('-------')
    print(f'Início: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print('-------')

    training_status = Training_status(
        user_id=user_id,
        start=start_training,
        status='working'
    )
    db.session.add(training_status)
    db.session.commit()
    training_status_id = training_status.id

    try:

        # Consulta no banco de dados filtrando pelo user_id e intervalo de data
        transactions = Transactions.query.filter_by(user_id=user_id).filter(
            Transactions.data_transaction.between(start_date, end_date)).all()

        # Criação do DataFrame a partir dos dados das transações
        transactions_df = pd.DataFrame([(t.id_transaction, t.id_item)
                                        for t in transactions], columns=['id_transaction', 'id_item'])

        # Chamar a função create_association_rules
        status_data = create_association_rules(
            user_id, transactions_df)

        # Salvar as informações de status na tabela Training_status
        Training_status.query.filter_by(
            id=training_status_id).update(status_data)
        db.session.commit()

        print(f'Fim: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        print('-------')

        response = {
            'start': start_training,
            'end': datetime.now(),
            'status': 200,
            'message': 'Association rules saved successfully.'
        }

        return jsonify(response), 200

    except Exception as e:
        # Atualizar informações de status em caso de erro
        status_data = {}
        status_data['end'] = datetime.now()
        status_data['status'] = 500
        status_data['message'] = str(e)

        # Salvar as informações de status na tabela Training_status
        Training_status.query.filter_by(
            id=training_status_id).update(status_data)
        db.session.commit()

        status_data['start'] = start_training

        print(f'Erro: {str(e)}')

        print('-------')
        print(f'Fim: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        print('-------')

        return jsonify(status_data), 500


def verify_api_key(api_key):
    """Verificação da apiKey"""
    user = User_api.query.filter_by(hash=api_key).first()

    if user:
        return user.user_id

    return False


@main.route('/v1/association-rules', methods=['POST'])
def get_association_rules_route():
    """Rota para consultar todas as regras de associação de um user_id"""
    api_key = request.headers.get('apiKey')

    user_id = verify_api_key(api_key)

    try:
        data = request.get_json()
    except ValueError:
        return jsonify({'status': 400, 'message': 'The request body is not valid JSON.', 'end': datetime.now()}), 400

    # Lista de campos obrigatórios
    required_fields = ['metric', 'order', 'limit']
    missing_fields = [field for field in required_fields if field not in data]

    if user_id:
        if missing_fields:
            missing_fields_str = ', '.join(missing_fields)
            error_message = f"The following fields are missing: {missing_fields_str}"
            return jsonify({'status': 400, 'message': error_message, 'end': datetime.now()}), 400

        metric = data.get('metric')
        order = data.get('order')
        limit = data.get('limit')

        mongo = Mongo('associations', 'associations_data')
        rules = mongo.get_association_rules(user_id, metric, order, limit)

        return rules

    return jsonify({'status': 401, 'message': 'Unauthorized', 'end': datetime.now()}), 401


@main.route('/v1/associations/', methods=['POST'])
def get_association_rules_by_antecedent_route():
    """Rota para consultar as regras de associação por antecedente de um user_id"""
    api_key = request.headers.get('apiKey')

    user_id = verify_api_key(api_key)

    try:
        data = request.get_json()
    except ValueError:
        return jsonify({'status': 400, 'message': 'The request body is not valid JSON.', 'end': datetime.now()}), 400

    # Lista de campos obrigatórios
    required_fields = ['metric', 'order', 'limit', 'antecedent']
    missing_fields = [field for field in required_fields if field not in data]

    if user_id:
        if missing_fields:
            missing_fields_str = ', '.join(missing_fields)
            error_message = f"The following fields are missing: {missing_fields_str}"
            return jsonify({'status': 400, 'message': error_message, 'end': datetime.now()}), 400
        metric = data.get('metric')
        order = data.get('order')
        limit = data.get('limit')
        antecedent = data.get('antecedent')

        mongo = Mongo('associations', 'associations_data')
        rules = mongo.get_association_rules_by_antecedent(
            user_id, antecedent, metric, order, limit)
        return rules

    return jsonify({'status': 401, 'message': 'Unauthorized', 'end': datetime.now()}), 401
