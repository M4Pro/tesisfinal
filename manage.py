from flask_script import Manager, Server
from aplicacion.app import app, db
from aplicacion.models import *
from getpass import getpass
server = Server(host="10.144.173.90", port=5000)
#server = Server(host="0.0.0.0", port=80)
manager = Manager(app)
manager.add_command("runserver", server)
app.config['DEBUG'] = True  # Ensure debugger will load.


@manager.command
def create_tables():
    "Create relational database tables."
    db.create_all()


@manager.command
def drop_tables():
    "Drop all project relational database tables. THIS DELETES DATA."
    db.drop_all()



@manager.command
def create_admin():
    alumno = {"nombre": input("Nombre completo:"),
              "username": input("Usuario:"),
              "password": getpass("Password:"),
               "email": input("Email:"),
               "Cursoid": 100000,
               "admin": True}
    alu = Alumnos(**alumno)
    db.session.add(alu)
    db.session.commit()

if __name__ == '__main__':
    manager.run()
