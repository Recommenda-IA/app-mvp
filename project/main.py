# main.py

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_paginate import Pagination, get_page_parameter
from flask_login import login_required, current_user
from .models.models import Database_access, Training_frequency, Transactions, User_api, Training_status
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import exc, create_engine
from hashlib import md5
from datetime import datetime
from mlxtend.frequent_patterns import apriori, association_rules
from pymongo import MongoClient, IndexModel, ASCENDING
import pandas as pd
import os
import json

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

        except exc.SQLAlchemyError as error_query:
            flash(str(error_query.orig) + " for parameters " +
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
            flash(str(error_query.orig) + " for parameters " +
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
            flash(str(error_query.orig) + " for parameters " +
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
            flash(str(error_query.orig) + " for parameters " +
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
    else:
        # Processar arquivo Excel
        # Requer a biblioteca pandas e openpyxl
        import pandas as pd
        df = pd.read_excel(arquivo)
        rotulos = df.columns.tolist()
        dados = df.values.tolist()

    if 'id_transaction' not in rotulos:
        flash('Sem rótulo id_transaction', 'error')
        return redirect(url_for('main.upload'))

    if 'id_item' not in rotulos:
        flash('Sem rótulo id_item', 'error')
        return redirect(url_for('main.upload'))

    if 'name_item' not in rotulos:
        flash('Sem rótulo name_item', 'error')
        return redirect(url_for('main.upload'))

    if 'customer_id' not in rotulos:
        flash('Sem rótulo customer_id', 'error')
        return redirect(url_for('main.upload'))

    if 'data_transaction' not in rotulos:
        flash('Sem rótulo data_transaction', 'error')
        return redirect(url_for('main.upload'))

    for linha in dados:
        if len(linha) != 5:
            flash('Dados incorretos. Verifique se os dados do arquivo seguem o padrão necessário ou se existem vírgulas entre os valores do arquivo.', 'error')
            return redirect(url_for('main.upload'))

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
            flash(str(error_query.orig) + " for parameters " +
                  str(error_query.params), 'error')

    flash('Dados salvos com sucesso!', 'success')
    return redirect(url_for('main.upload'))


@main.route('/view-data')
@login_required
def view_data():

    if Transactions.query.filter_by(user_id=current_user.id).count() == 0:
        message = 'Sem registros.'
        return render_template('dashboard/view-data.html', name=current_user.name, message=message)
    else:
        page = request.args.get(get_page_parameter(), type=int, default=1)
        per_page = 30

        pagination = Transactions.query.order_by(Transactions.created_at.desc()).paginate(
            page=page, per_page=per_page)
        transactions = pagination.items
        pagination_range = pagination.iter_pages(
            left_edge=2,
            left_current=2,
            right_current=3,
            right_edge=2
        )

        return render_template('dashboard/view-data.html', name=current_user.name, transactions=transactions, pagination=pagination, pagination_range=pagination_range)


@main.route('/data-management')
def data_management():

    return render_template('dashboard/data-management.html', name=current_user.name)


@main.route('/data-management/delete', methods=['POST'])
def data_management_delete():
    try:
        db_delete = request.form.get('db_delete')
        if db_delete == 'deletar informações':
            Transactions.query.filter_by(
                user_id=current_user.id).delete()
            db.session.commit()

            flash('Informações de transações excluídas com sucesso.', 'success')
        else:
            flash(
                'Por favor, digite "deletar informações" para confirmar a exclusão de informações.', 'error')

    except exc.SQLAlchemyError as error_query:
        flash(str(error_query.orig) + " for parameters " +
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
        return render_template('dashboard/api-users.html', name=current_user.name, data_users=data_users)


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
            flash(str(error_query.orig) + " for parameters " +
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
            flash(str(error_query.orig) + " for parameters " +
                  str(error_query.params), 'error')

    return redirect(url_for('main.api_users'))


# -------- TREINAMENTO -------------------

# Configuração do MongoDB
client = MongoClient(os.environ['MONGODBURL'])
db_mongo = client['associations']
# Configurar o índice para a coleção
collection = db_mongo['associations_data']
collection.create_indexes([
    IndexModel([('user_id', ASCENDING)]),
    IndexModel([('antecedents', ASCENDING)]),
    IndexModel([('support', ASCENDING)]),
    IndexModel([('confidence', ASCENDING)]),
    IndexModel([('lift', ASCENDING)]),
    IndexModel([('consequent', ASCENDING)])
])

# Função para buscar, filtrar e salvar as regras de associação no MongoDB


def save_association_rules(user_id, start_date, end_date):
    # Armazenar informações de status de treinamento
    status_data = {
        'start': datetime.now(),
        'end': None,
        'status': None,
        'message': None
    }

    try:
        # Consulta no banco de dados filtrando pelo user_id e intervalo de data
        transactions = Transactions.query.filter_by(user_id=user_id).filter(
            Transactions.data_transaction.between(start_date, end_date)).all()

        # Criação do DataFrame a partir dos dados das transações
        df = pd.DataFrame([(t.id_transaction, t.id_item)
                           for t in transactions], columns=['id_transaction', 'id_item'])

        tabulacao_itens = (pd.crosstab(df['id_transaction'], df['id_item'])
                           .clip(upper=1)
                           .reset_index()
                           .rename_axis(None, axis=1))

        if 'id_transaction' in tabulacao_itens.columns:
            del tabulacao_itens['id_transaction']

        # Aplicação do algoritmo Apriori para encontrar os itens frequentes
        frequent_itemsets = apriori(
            tabulacao_itens.astype('bool'), min_support=0.1, use_colnames=True)

        # Criação das regras de associação a partir dos itens frequentes
        rules = association_rules(
            frequent_itemsets, metric="support", min_threshold=0.1)

        # Ordenar cada resultado de antecedente em ordem crescente
        rules['antecedents'] = rules['antecedents'].apply(
            lambda x: tuple(sorted(x)))

        # Remover regras com antecedentes duplicados
        rules = rules.drop_duplicates(subset='antecedents')

        # Salvando as regras de associação no MongoDB
        unsaved_records = []
        record_buffer = []
        for _, rule in rules.iterrows():
            association_data = {
                'user_id': user_id,
                'antecedents': tuple(rule['antecedents']),
                'consequent': tuple(rule['consequents']),
                'support': rule['support'],
                'confidence': rule['confidence'],
                'lift': rule['lift']
            }

            record_buffer.append(association_data)

            # Inserir registros acumulados quando atingir 1000
            if len(record_buffer) == 1000:
                try:
                    collection.insert_many(record_buffer)
                except Exception as e:
                    unsaved_records.extend(record_buffer)

                record_buffer = []

        # Inserir registros remanescentes
        if record_buffer:
            try:
                collection.insert_many(record_buffer)
            except Exception as e:
                unsaved_records.extend(record_buffer)

        # Salvando registros não salvos em um arquivo JSON
        if unsaved_records:
            current_date = datetime.now().strftime('%Y-%m-%d')
            filename = f"{user_id}_{current_date}.json"
            filepath = os.path.join("json_temp", filename)
            with open(filepath, 'w') as file:
                json.dump(unsaved_records, file)

        # Atualizar informações de status
        status_data['end'] = datetime.now()
        status_data['status'] = 'success'

    except Exception as e:
        # Atualizar informações de status em caso de erro
        status_data['end'] = datetime.now()
        status_data['status'] = 'error'
        status_data['message'] = str(e)

    # Salvar informações de status na tabela training_status
    Training_status.query.filter_by(user_id=user_id).update(status_data)
    db.session.commit()

# Rota para executar a função save_association_rules


@main.route('/association-rules', methods=['POST'])
def run_association_rules():

    inicio = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    user_id = 1
    start_date = '2000-06-30'
    end_date = '2003-07-02'

    print('-------')
    print(f'Início: {inicio}')
    print('-------')

    save_association_rules(user_id, start_date, end_date)

    print(f'Fim: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print('-------')

    return 'Association rules saved successfully.'
