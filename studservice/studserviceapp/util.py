import datetime

def get_current_semester():
    trenutnaGodina = datetime.datetime.now().year
    trenutniMesec = datetime.datetime.now().month
    if trenutniMesec <= 2 or trenutniMesec >= 10:
        trenutniSemestar = 'neparni'
    else:
        trenutniSemestar = 'parni'

    return trenutniSemestar