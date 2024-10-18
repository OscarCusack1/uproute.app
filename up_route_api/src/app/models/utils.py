
def convert_time_to_minutes(time):
    if time:
        return int(time.split(':')[0]) * 60 + int(time.split(':')[1])
    return None