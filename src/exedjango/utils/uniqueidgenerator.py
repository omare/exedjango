import uuid

class UniqueIdGenerator(object):
    '''UUID support for legacy exporters'''
    def generate(self):
        return uuid.uuid4()