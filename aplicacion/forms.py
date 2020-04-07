from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DecimalField, IntegerField,\
    TextAreaField, SelectField, PasswordField
from wtforms.fields.html5 import EmailField
from flask_wtf.file import FileField
from wtforms.validators import Required


class formCurso(FlaskForm):
    nombre = StringField("Nombre:",
                         validators=[Required("Tienes que introducir el dato")]
                         )
    submit = SubmitField('Enviar')
    
class formEjercicio(FlaskForm):
    titulo = StringField("Titulo:",
                         validators=[Required("Tienes que introducir el dato")]
                         )

    planteamiento = TextAreaField("Planteamiento:" )
    Cursoid = SelectField("Curso:", coerce=int)
    submit = SubmitField('Enviar')




class formEncuesta(FlaskForm):
    nombre = StringField("Nombre:",
                         validators=[Required("Tienes que introducir el dato")]
                         )
    Cursoid = SelectField("Curso:", coerce=int)
    submit = SubmitField('Enviar')


class formActividad(FlaskForm):
    nombre = StringField("Nombre:",
                         validators=[Required("Tienes que introducir el dato")]
                         )
    Cursoid = SelectField("Curso:", coerce=int)
    submit = SubmitField('Enviar')


class formPregunta(FlaskForm):
    nombre = StringField("Nombre:",
                         validators=[Required("Tienes que introducir el dato")]
                         )
    Encuestaid = SelectField("Encuesta:", coerce=int)
    submit = SubmitField('Enviar')

class formPreguntaE(FlaskForm):
    nombre = StringField("Nombre:",
                         validators=[Required("Tienes que introducir el dato")]
                         )
    Encuestaid = SelectField("Encuesta:", coerce=int)
    submit = SubmitField('Enviar')

class formPreguntaA(FlaskForm):
    nombre = StringField("Nombre:",
                         validators=[Required("Tienes que introducir el dato")]
                         )
    Actividadid = SelectField("Actividad:", coerce=int)
    submit = SubmitField('Enviar')
    
class formAlumnoED(FlaskForm):  
    username = StringField('Nombre de Usuario', validators=[Required()])
    password = PasswordField('Contraseña', validators=[Required()])
    nombre = StringField('Nombre completo')
    email = EmailField('Email')
    submit = SubmitField('Guardar')
    

class formAlumno(FlaskForm):
    username = StringField('Login', validators=[Required()])
    password = PasswordField('Password', validators=[Required()])
    nombre = StringField('Nombre completo')
    email = EmailField('Email')
    submit = SubmitField('Aceptar')
    
    Cursoid = SelectField("Curso:", coerce=int)
    submit = SubmitField('Enviar')


class formAlumnoE(FlaskForm):
       
    nombre = StringField('Nombre completo')
    email = EmailField('Email')
    submit = SubmitField('Aceptar')
    
    Cursoid = SelectField("Curso:", coerce=int)
    submit = SubmitField('Enviar')
class formSINO(FlaskForm):      
  	si = SubmitField('Si') 
  	no = SubmitField('No') 


class LoginForm(FlaskForm):
  	username = StringField('Login', validators=[Required()])
  	password = PasswordField('Password', validators=[Required()])
  	submit = SubmitField('Entrar')





class FormChangePassword(FlaskForm):
    password = PasswordField('Password', validators=[Required()])
    submit = SubmitField('Aceptar')
