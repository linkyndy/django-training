class MasterSlaveRouter(object):
    def db_for_read(self, model, **hints):
        return 'slave'

    def db_for_write(self, model, **hints):
        return 'master'

    def allow_relation(self, obj1, obj2, **hints):
        dbs = ['master', 'slave']
        if obj1.state.db in dbs and \
           obj2.state.db in dbs:
            return True
        return None

    def allow_syncdb(self, db, model):
        return True
