import datetime

def get_now_timestamp():
    """Get the current utc timestamp.

    Returns:
        int: Now.
    """
    return int(datetime.datetime.now(datetime.timezone.utc).timestamp())


def timestamp_as_datetime_string(timestamp: int):
    """Return the timestamp as a datetime string
    
    Args:
        timestamp (int): The UNIX timestamp.

    Returns:
        str: The datetime string.
    """
    return datetime.datetime.fromtimestamp(timestamp, datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")