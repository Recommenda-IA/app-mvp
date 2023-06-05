import pandas as pd
import random

# Gerando um conjunto de dados aleatório
transaction_ids = range(1, 11)
item_ids = range(1, 6)
data = []

for transaction_id in transaction_ids:
    num_items = random.randint(1, 3)
    items = random.sample(item_ids, num_items)
    data.append({'transaction_id': transaction_id, 'item_ids': items})

df = pd.DataFrame(data)

# Exibindo o conjunto de dados de teste
print(df.head())
