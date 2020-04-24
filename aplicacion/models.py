from sqlalchemy import Boolean, Column, ForeignKey
from sqlalchemy import DateTime, Integer, String, Text, Float
from sqlalchemy.orm import relationship
from aplicacion.app import db
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.sql.schema import Table


class Preguntas(db.Model):
    """Preguntas de las Encuestas"""
    __tablename__ = 'preguntas'
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100))
    respuesta = Column(String(100))
    cantidad_resp=Column(Integer)
    Encuestaid = Column(Integer, ForeignKey('encuestas.id'), nullable=False)
    encuesta = relationship("Encuestas", backref="Preguntas")
    
    def __repr__(self):
        return (u'<{self.__class__.__name__}: {self.id}>'.format(self=self))


class PreguntasA(db.Model):
    """Preguntas de las Encuestas"""
    __tablename__ = 'preguntasA'
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100))
    respuesta = Column(String(100))
    cantidad_resp=Column(Integer)
    Actividadid = Column(Integer, ForeignKey('actividades.id'), nullable=False)
    actividad = relationship("Actividades", backref="Preguntas")
    
    def __repr__(self):
        return (u'<{self.__class__.__name__}: {self.id}>'.format(self=self))

class Cursos(db.Model):
    """Cursos de los Alumnos"""
    __tablename__ = 'cursos'
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100))
    alumnos = relationship("Alumnos", cascade="all, delete-orphan", backref="Cursos",lazy='dynamic')
    encuestas = relationship("Encuestas", cascade="all, delete-orphan", backref="Cursos",lazy='dynamic')
    actividades = relationship("Actividades", cascade="all, delete-orphan", backref="Cursos",lazy='dynamic')
    image = relationship("Image", cascade="all, delete-orphan", backref="Cursos",lazy='dynamic')
    ejercicios = relationship("Ejercicios", cascade="all, delete-orphan", backref="Cursos",lazy='dynamic')
    def __repr__(self):
        return (u'<{self.__class__.__name__}: {self.id}>'.format(self=self))

class Encuestas(db.Model):
    """Encuestas de los Alumnos"""
    __tablename__ = 'encuestas'
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100))
    Cursoid = Column(Integer, ForeignKey('cursos.id'), nullable=False)
    curso = relationship("Cursos", backref="Encuestas")
    preguntas = relationship("Preguntas", cascade="all, delete-orphan", backref="Encuestas",lazy='dynamic')
    ptajes = db.relationship('Puntaje', backref='enc')
    
    def __repr__(self):
        return (u'<{self.__class__.__name__}: {self.id}>'.format(self=self))

class Actividades(db.Model):
    """Actividades de los Alumnos"""
    __tablename__ = 'actividades'
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100))
    Cursoid = Column(Integer, ForeignKey('cursos.id'), nullable=False)
    curso = relationship("Cursos", backref="Actividades")
    preguntas = relationship("PreguntasA", cascade="all, delete-orphan", backref="Actividades",lazy='dynamic')
    ptajesA = db.relationship('PuntajeA', backref='act')

    def __repr__(self):
        return (u'<{self.__class__.__name__}: {self.id}>'.format(self=self))

class Ejercicios(db.Model):
    """Ejercicios de los Alumnos"""
    __tablename__ = 'ejercicios'
    id = Column(Integer, primary_key=True)
    titulo = Column(String(100))
    planteamiento = Column(String(100))
    Cursoid = Column(Integer, ForeignKey('cursos.id'), nullable=False)
    curso = relationship("Cursos", backref="Ejercicios")

    def __repr__(self):
        return (u'<{self.__class__.__name__}: {self.id}>'.format(self=self))


enc_alu=Table('enc_alu',db.metadata,
        Column('id_alumno',Integer,ForeignKey('alumnos.id')),
        Column('id_encuesta',Integer,ForeignKey('encuestas.id'))
)
act_alu=Table('act_alu',db.metadata,
        Column('id_alumno',Integer,ForeignKey('alumnos.id')),
        Column('id_actividad',Integer,ForeignKey('actividades.id'))

)
class PuntajeE(db.Model):
    puntajeE_id = db.Column(db.Integer, primary_key=True)
    notaI = db.Column(Float)
    notaD = db.Column(Float)
    notaC = db.Column(Float)
    
    introduccion = Column(String(100))
    desarrollo = Column(String(100))
    conclusion = Column(String(100))
    puntaje_total = db.Column(db.Float)
    alu_id = db.Column(db.Integer, db.ForeignKey('alumnos.id'))
    eje_id = db.Column(db.Integer, db.ForeignKey('ejercicios.id'))

class Puntaje(db.Model):
    puntaje_id = db.Column(db.Integer, primary_key=True)
    puntaje_total = db.Column(db.Float)
    alu_id = db.Column(db.Integer, db.ForeignKey('alumnos.id'))
    enc_id = db.Column(db.Integer, db.ForeignKey('encuestas.id'))
    
class Image(db.Model):
    image_id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(80), nullable=False)
    Cursoid = db.Column(db.Integer, db.ForeignKey("cursos.id"), nullable=False)
    uploader = db.Column(db.String(50), nullable=True)

class PuntajeA(db.Model):
    puntajeA_id = db.Column(db.Integer, primary_key=True)
    puntaje_total = db.Column(db.Float)
    alu_id = db.Column(db.Integer, db.ForeignKey('alumnos.id'))
    act_id = db.Column(db.Integer, db.ForeignKey('actividades.id'))

class Alumnos(db.Model):
    """Alumnos"""
    __tablename__ = 'alumnos'
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    username = Column(String(100),nullable=False)
    password_hash = Column(String(128),nullable=False)
    nombre = Column(String(200),nullable=False)
    email = Column(String(200),nullable=False)
    Cursoid = Column(Integer, ForeignKey('cursos.id'), nullable=False)
    curso = relationship("Cursos", backref="Alumnos")
    admin = Column(Boolean, default=False)
    encuesta_resp=relationship("Encuestas",secondary=enc_alu,backref="encuesta_resp", lazy= 'dynamic')
    actividad_resp=relationship("Actividades",secondary=act_alu,backref="actividad_resp", lazy= 'dynamic')
    ptajes = db.relationship('Puntaje', backref='alu')
    ptajesA = db.relationship('PuntajeA', backref='alu')
    ptajesE = db.relationship('PuntajeE', backref='alu')
    def __repr__(self):
        return (u'<{self.__class__.__name__}: {self.id}>'.format(self=self))	
    
    @property 
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter 
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password): 
        return check_password_hash(self.password_hash, password)

    # Flask-Login integration 
    def is_authenticated(self): 
        return True 

    def is_active(self): 
        return True 

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def is_admin(self):
        return self.admin

