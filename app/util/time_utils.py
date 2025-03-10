import datetime

def get_now_timestamp():
    """Get the current utc timestamp.

    Returns:
        int: Now.
    """
    return int(datetime.datetime.now(datetime.timezone.utc).timestamp())