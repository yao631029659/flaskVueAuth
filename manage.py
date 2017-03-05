from api2 import db,app
from model import Users,Customers
from flask_script import Manager,Server,Shell

manager=Manager(app)

manager.add_command('server',Server())

@manager.shell
def make_shell_context():
    return dict(app=app,db=db,Users=Users,Customers=Customers)

if __name__=="__main__":
    manager.run()