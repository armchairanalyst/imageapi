import sys,traceback,string, random

def view_traceback():
    ex_type, ex, tb = sys.exc_info()
    traceback.print_tb(tb)
    del tb


def GenerateRandomString(len):
    chars = string.ascii_lowercase
    return ''.join(random.choice(chars) for x in range(len))