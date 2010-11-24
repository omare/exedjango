'''
Some convinience decorators
'''

def alters_data(func):
    '''Sets alters_data for a function, so it can't be accessed from
a template'''
    
    def new_func(*args, **kwargs):
        func.alters_data = True
    return func
