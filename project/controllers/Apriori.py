import numpy as np
import pandas as pd
import pickle
from mlxtend.frequent_patterns import apriori, association_rules
from sqlalchemy import create_engine
from sqlalchemy import exc
from datetime import datetime


class Apriori:
    def __init__(self):
        pass

    def executa(produtos_tabulados, min_suport, use_colnames, metric, min_threshold, sort_values, ascending):
        frq_items = apriori(produtos_tabulados.astype('bool'),
                            min_support=0.01, use_colnames=True)
        regras = association_rules(frq_items, metric="lift", min_threshold=10)
        return regras
