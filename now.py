from datetime import datetime

def get_time():
    return str(datetime.now().strftime('%I:%M%p %m-%d-%y'))