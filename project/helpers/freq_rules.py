from pymongo import MongoClient, ASCENDING
from pymongo.operations import IndexModel
from datetime import datetime
import pandas as pd
from mlxtend.frequent_patterns import fpgrowth
from mlxtend.frequent_patterns import association_rules
import os
import json


def remove_redundant_rules(rules):
    # Ordenar as regras por confiança em ordem decrescente
    rules = rules.sort_values(by='confidence', ascending=False)

    # Criar um conjunto vazio para armazenar as regras não redundantes
    non_redundant_rules = set()

    # Percorrer cada regra
    for _, rule in rules.iterrows():
        antecedents = rule['antecedents']

        # Verificar se a regra é subconjunto de alguma regra já considerada não redundante
        is_redundant = False
        for non_redundant_rule in non_redundant_rules:
            if antecedents.issubset(non_redundant_rule):
                is_redundant = True
                break

        # Adicionar a regra ao conjunto de regras não redundantes, se não for redundante
        if not is_redundant:
            non_redundant_rules.add(antecedents)

    # Filtrar as regras originais mantendo apenas as regras não redundantes
    filtered_rules = rules[rules['antecedents'].apply(
        lambda x: x in non_redundant_rules)]

    return filtered_rules


def get_association_rules(user_id, transactions_df):
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

    # Armazenar informações de status de treinamento
    status_data = {
        'end': None,
        'status': None,
        'message': None
    }

    try:
        df = transactions_df.copy()

        tabulacao_itens = (pd.crosstab(df['id_transaction'], df['id_item'])
                           .clip(upper=1)
                           .reset_index()
                           .rename_axis(None, axis=1))

        if 'id_transaction' in tabulacao_itens.columns:
            del tabulacao_itens['id_transaction']

        # Aplicação do algoritmo Apriori para encontrar os itens frequentes
        frequent_itemsets = fpgrowth(
            tabulacao_itens.astype('bool'), min_support=0.15, use_colnames=True)

        # Criação das regras de associação a partir dos itens frequentes
        rules = association_rules(
            frequent_itemsets, metric="support", min_threshold=0.1)

        # Remover regras redundantes
        rules = remove_redundant_rules(rules)

        # Ordenar cada resultado de antecedente em ordem crescente
        rules['antecedents'] = rules['antecedents'].apply(
            lambda x: tuple(sorted(x)))

        # Remover regras com antecedentes duplicados
        # rules = rules.drop_duplicates(subset='antecedents')

        # Salvando as regras de associação no MongoDB
        unsaved_records = []
        record_buffer = []
        for _, rule in rules.iterrows():
            association_data = {
                'user_id': user_id,
                'antecedents': tuple(rule['antecedents']),
                'consequents': tuple(rule['consequents']),
                'support': rule['support'],
                'confidence': rule['confidence'],
                'lift': rule['lift']
            }

            record_buffer.append(association_data)

            # Inserir registros acumulados quando atingir 1000
            if len(record_buffer) == 10000:
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

    return status_data
