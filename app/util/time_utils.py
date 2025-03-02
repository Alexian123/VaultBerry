import datetime

def get_now_timestamp():
    return int(datetime.datetime.now(datetime.timezone.utc).timestamp())