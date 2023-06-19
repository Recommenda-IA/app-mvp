from pytz import timezone
import datetime


def convert_to_sao_paulo_time(utc_time):
    utc = timezone('UTC')
    sao_paulo = timezone('America/Sao_Paulo')
    utc_time = utc.localize(utc_time)
    sao_paulo_time = utc_time.astimezone(sao_paulo)
    return sao_paulo_time
