from flask import Flask,send_from_directory, render_template,flash, redirect, url_for, request, abort,\
    session
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from aplicacion import config
from aplicacion.forms import formCurso, formAlumno,formArchivo,formPreguntaE , formSINO , LoginForm  , FormChangePassword ,formAlumnoE ,formAlumnoED ,formEncuesta , formPregunta, formPreguntaA  , formActividad , formEjercicio
from werkzeug.utils import secure_filename
from flask_login import LoginManager, login_user, logout_user, login_required,\
    current_user
import os
import urllib.parse, hashlib
app = Flask(__name__)
app.config.from_object(config)
Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
ALLOWED_EXTENSIONS = set(["xls", "jpg", "jpge", "gif", "pdf","docx"])


def allowed_file(filename):

    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/uploads/<filename>')
def uploaded_file(filename):

    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/files')
def get_all_files():
    from aplicacion.models import Image , Alumnos , Cursos
    print("el alumno actual es ", current_user.username)
    alumnos=Alumnos.query.filter_by(id=current_user.id)
    archivos=Image.query.all()
    totalarchivos=len(archivos)
    if totalarchivos ==0:
        return render_template("nohay.html")

    if not current_user.is_admin():
        cursos=Cursos.query.filter_by(id=alumnos[0].Cursoid)
        files = Image.query.filter_by(Cursoid=alumnos[0].Cursoid)
    else:
        files=Image.query.all()
        cursos=Cursos.query.all()
        cursos[0].nomnbre="Todos"
        
    
   

    return render_template("myfiles.html", files=files, cursos=cursos)

@app.route('/archivos', methods=["GET", "POST"])
def archivos():
    from aplicacion.models import Cursos , Image, Alumnos
    alumnos=Alumnos.query.filter_by(id=current_user.id)
    
    cursos = Cursos.query.all()
    print(len(cursos))
    cant_cursos = len(cursos)

    if request.method == "POST":

        selectarchivo = request.form["selectarchivo"]
        print("El id del curso seleccionado es: ", selectarchivo)

        if "ourfile" not in request.files:
            return "The form has no file part"

        f = request.files["ourfile"]
        if f.filename=="":
            return "no file selected"
        if f and allowed_file(f.filename):
            filename = secure_filename(f.filename)
            file_to_db = Image(filename=filename, Cursoid=selectarchivo,uploader=current_user.username)
            db.session.add(file_to_db)
            db.session.commit()
            f.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            return render_template("archivos.html", cursos=cursos, cant_cursos=cant_cursos)
    return render_template("archivos.html", cursos=cursos, cant_cursos=cant_cursos)


@app.route('/upload', methods=["GET", "POST"])
def upload():
    if request.method == "POST":
            if "file" not in request.files:
                flash("No file part.", "alert-danger")
                return redirect(request.url)
            file = request.files["file"]
            if file.filename == "":
                flash("No selected file.", "alert-warning")
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                
                file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            return redirect(url_for("get_file",filename=filename))
    return render_template("archivos.html")

@app.route('/uploads/<filename>')
def get_file():

    return send_from_directory(app.config["UPLOAD_FOLDER"],filename)

@app.route('/')
@app.route('/curso/<id>')
def inicio(id='0'):
    from aplicacion.models import Alumnos, Cursos , Encuestas , Preguntas
    curso = Cursos.query.get(id)
    # Control de permisos
    #print("aaaa", current_user)
    try:
        if not current_user.is_admin():
            return redirect(url_for('inicioAlum', username=current_user.username))
    except Exception as e:
        pass
    

    if id == '0':
        alumnos = Alumnos.query.filter_by(Cursoid=id)
        print("no seleccione nada")
    else:
        print("si seleccione")
        alumnos = Alumnos.query.filter_by(Cursoid=id)
    cursos = Cursos.query.all()

    if id == '0':
        encuestas = Encuestas.query.all()
    else:
        encuestas = Encuestas.query.filter_by(Cursoid=id)
    cursos = Cursos.query.all()
    
    if id == '0':
        preguntas = Preguntas.query.all()
    else:
        preguntas = Preguntas.query.filter_by(Encuestaid=id)
    encuesta = Encuestas.query.all()

    return render_template("inicio.html", alumnos=alumnos,cursos=cursos, curso=curso,encuestas=encuestas, preguntas=preguntas)

@app.route('/cursos')
def cursos():
    from aplicacion.models import Cursos
    cursos = Cursos.query.all()
    return render_template("cursos.html", cursos=cursos)

@app.route('/inicioAlum/<username>', methods=["get", "post"])

def inicioAlum(username):
    from aplicacion.models import Alumnos , Encuestas , Cursos , Actividades, Ejercicios ,PuntajeE ,Puntaje,PuntajeA
    dataTable = []
    dataTable2 = []
    dataTable3 = []
    """alumnos= Alumnos.query.all()
    actividades= Actividades.query.all()
    ejercicios= Ejercicios.query.all()
    cursos =Cursos.query.all()
    encuestas =Encuestas.query.all()"""
    alum=Alumnos.query.filter_by(username=username)
    cur=Cursos.query.filter_by(id=alum[0].Cursoid)
    encuestasalu=Encuestas.query.filter_by(Cursoid=cur[0].id)
    actividadesalu=Actividades.query.filter_by(Cursoid=cur[0].id)
    ejerciciosalu=Ejercicios.query.filter_by(Cursoid=cur[0].id)

    puntajercicio=PuntajeE.query.filter_by(alu_id=alum[0].id)
    largopun=puntajercicio.count()
    print("EL LARGO DEL PUNTAJE",largopun)
    for index in range(0,largopun):
        print(index)
        ejeAux = Ejercicios.query.filter_by(id=puntajercicio[index].eje_id)
        aluAux = Alumnos.query.filter_by(id=puntajercicio[index].alu_id)
        if puntajercicio[index].puntaje_total==None:
            puntajercicio[index].puntaje_total=0;
            print("es none")
            dataTable.append(
                        {   'nombreAlumno': aluAux[0].nombre,
                            'nombreEjercicio': ejeAux[0].titulo,
                            'puntajeTotal': "Falta Calificar"
                        }
                    )
        else:
            dataTable.append(
                        {   'nombreAlumno': aluAux[0].nombre,
                            'nombreEjercicio': ejeAux[0].titulo,
                            'puntajeTotal': puntajercicio[index].puntaje_total
                        }
                    )

    puntaEncuesta=Puntaje.query.filter_by(alu_id=alum[0].id)
    largoenct=puntaEncuesta.count()
    print("existen un total de encuestas ",largoenct)
    for index in range(0,largoenct):
        print(puntaEncuesta[index].enc_id)


    for index in range(0,largoenct):
        print("este es el for numero",puntaEncuesta[index].enc_id)


        encAux = Encuestas.query.filter_by(id=puntaEncuesta[index].enc_id)
        aluAux = Alumnos.query.filter_by(id=puntaEncuesta[index].alu_id)
        
           
       
        dataTable2.append(
                    {   'nombreEncuesta': encAux[0].nombre,
                        'puntajeTotal': puntaEncuesta[index].puntaje_total
                    }
                )

    puntaTest=PuntajeA.query.filter_by(alu_id=alum[0].id)
    largopuntA=puntaTest.count()

    for index in range(0,largopuntA):
        print(index)
        testAux = Actividades.query.filter_by(id=puntaTest[index].act_id)
        aluAux = Alumnos.query.filter_by(id=puntaTest[index].alu_id)
        
           
       
        dataTable3.append(
                    {   'nombreTest': testAux[0].nombre,
                        'puntajeTotal': puntaTest[index].puntaje_total
                    }
                )


    return render_template("inicioAlum.html",dataTable=dataTable,dataTable2=dataTable2,dataTable3=dataTable3,cur=cur,alum=alum,encuestasalu=encuestasalu,actividadesalu=actividadesalu,ejerciciosalu=ejerciciosalu, puntajercicio=puntajercicio)

    

@app.route('/calificaciones')
def calificaciones():
    print("calificaciones")
    from aplicacion.models import Encuestas, Alumnos, Actividades, Puntaje

    dataTable = []

    encuestas = Encuestas.query.all()
    alumnos = Alumnos.query.all()
    puntaje = Puntaje.query.all()
    largopuntaje=len(puntaje)
    print("existen ",len(puntaje))
    for index in range(0,len(puntaje)):
        print(index)
        encAux = Encuestas.query.filter_by(id=puntaje[index].enc_id)
        aluAux = Alumnos.query.filter_by(id=puntaje[index].alu_id)
        
           
       
        dataTable.append(
                    {   'nombreAlumno': aluAux[0].nombre,
                        'nombreEncuesta': encAux[0].nombre,
                        'puntajeTotal': puntaje[index].puntaje_total
                    }
                )
    

    return render_template("calificaciones.html", dataTable = dataTable)

@app.route('/calificar')
@login_required
def calificar():
    print("calificar")
    from aplicacion.models import  Alumnos, Ejercicios, PuntajeE
    if not current_user.is_admin():
        abort(404)

    dataTable = []

    ejercicios = Ejercicios.query.all()
    alumnos = Alumnos.query.all()
    puntaje = PuntajeE.query.all()
    print(puntaje)

    
      

    for index in range(0,len(puntaje)):
        print("ESTOY EN CALIFICAR")
        print(index)
        try:
            ejeAux = Ejercicios.query.filter_by(id=puntaje[index].eje_id)
       
            aluAux = Alumnos.query.filter_by(id=puntaje[index].alu_id)
            puntTotal= (puntaje[index].puntaje_total)
            #print(puntaje[index].ejeAux[0].nombre, aluAux[0].nombre)
            if puntTotal==None:
                dataTable.append(
                            {   'nombreAlumno': aluAux[0].nombre,
                                'tituloEjercicio': ejeAux[0].titulo,
                                'idAlumno': aluAux[0].id,
                                'idEjercicio': ejeAux[0].id,                   
                                'puntTotal'  :  "Por Calificar"          }
                        )
            
            
            else:
                dataTable.append(
                            {   'nombreAlumno': aluAux[0].nombre,
                                'tituloEjercicio': ejeAux[0].titulo,
                                'idAlumno': aluAux[0].id,
                                'idEjercicio': ejeAux[0].id,                   
                                'puntTotal'  :  puntTotal          }
                        )
        except Exception as e:
            pass
        
    

    return render_template("calificar.html", dataTable = dataTable)



@app.route('/calificacionesA')
def calificacionesA():
    print("calificaciones")
    from aplicacion.models import  Alumnos, Actividades, PuntajeA
      
    dataTable = []

    actividades = Actividades.query.all()
    alumnos = Alumnos.query.all()
    puntaje = PuntajeA.query.all()
    print(len(puntaje))
    for index in range(0,len(puntaje)):
        actAux = Actividades.query.filter_by(id=puntaje[index].act_id)
        aluAux = Alumnos.query.filter_by(id=puntaje[index].alu_id)
        
        dataTable.append(
                    {   'nombreAlumno': aluAux[0].nombre,
                        'nombreActividad': actAux[0].nombre,
                        'puntajeTotal': puntaje[index].puntaje_total
                    }
                )
    

    return render_template("calificacionesA.html", dataTable = dataTable)

@app.route('/encuestas')
def encuestas():
    from aplicacion.models import Encuestas , Preguntas
    encuestas=Encuestas.query.all()
    preguntas=Preguntas.query.all()
    return render_template("encuestas.html", encuestas=encuestas, preguntas=preguntas)

@app.route('/ejercicios')
def ejercicios():
    from aplicacion.models import Ejercicios ,Alumnos
    alum=Alumnos.query.all()
    ejercicios=Ejercicios.query.all()
    print(ejercicios)


    return render_template("ejercicios.html", ejercicios=ejercicios,alum=alum)
    
@app.route('/ejerciciosA/<id_ejercicio>', defaults={'id_ejercicio': 1}, methods=["GET", "POST"])
@app.route('/ejerciciosA/<id_ejercicio>', methods=["GET", "POST"])
@login_required
def ejerciciosA(id_ejercicio):
    from aplicacion.models import Ejercicios, PuntajeE, Alumnos
    
    print(id_ejercicio[0])
    ejercicios=Ejercicios.query.filter_by(id=id_ejercicio[0])
    #ejercicios[0]
    body_data = []
    print("ntes del post")
    print(request.method)
    if request.method =='POST':
        print("despues del post")
        intro_data = request.form['introduccion']
        desa_data = request.form['desarrollo']
        conclu_data = request.form['conclusion']
        print(intro_data, desa_data, conclu_data)
        print("current_user", current_user.id)
        #alumno_data = Alumno.query.filter_by(nombre=)
        compare = PuntajeE.query.all()
        for index in range(0, len(compare)):
            if compare[0].alu_id == current_user.id and compare[0].eje_id == ejercicios[0].id:
                return redirect(url_for('inicioAlum', username=current_user.username))

        dataTotal = PuntajeE(introduccion=intro_data, desarrollo=desa_data, conclusion=conclu_data, eje_id=ejercicios[0].id, alu_id=int(current_user.id))
        db.session.add(dataTotal)
        db.session.commit()
        
        print("guardado ok")
        #body_data = PuntajeE.query.join()
    
    body_data = db.session.query(PuntajeE).join(Alumnos).join(Ejercicios).filter(PuntajeE.alu_id == current_user.id).filter(PuntajeE.eje_id == ejercicios[0].id).all()
    
    try:
        print("body_data1")
        body_data = body_data[0]
        print("info intro", body_data.introduccion)
        if body_data.introduccion == "":
            flag_respuesta = False
        else:
            flag_respuesta = True
    except Exception as e:
        print("body_data2")
        body_data = []
        flag_respuesta = False
    #print(body_data[0].introduccion)


    return render_template("ejerciciosA.html", ejercicios=ejercicios[0], body_data=body_data, flag_respuesta=flag_respuesta)

@app.route('/ejerciciosADM/<id_ejercicio>/<id_alum>', defaults={'id_ejercicio': 1, 'id_alum': 1}, methods=["GET", "POST"])
@app.route('/ejerciciosADM/<id_ejercicio>/<id_alum>', methods=["GET", "POST"])
@login_required
def ejerciciosADM(id_ejercicio, id_alum):
    from aplicacion.models import Ejercicios, PuntajeE, Alumnos
    #listpuntaje=PuntajeE.query.all()
    dataTable = []

    #info_calif = db.session.query(Alumnos).join(PuntajeE).join(Ejercicios).filter(Alumnos.id == id_alum).filter(Ejercicios.id == id_ejercicio).all()
    info_calif = db.session.query(Alumnos, PuntajeE, Ejercicios).filter(Alumnos.id == id_alum).filter(Ejercicios.id == id_ejercicio).filter(PuntajeE.alu_id == id_alum).filter(PuntajeE.eje_id == id_ejercicio)
    #info_calif = info_calif.filter(Alumnos.id == id_alum)
    print("ANTES DEL PRINT")
    #print(info_calif.filter(Ejercicios.id == id_ejercicio)[0])
    print(info_calif[0])
    #for index in range(0, len(listpuntaje)):
           
    #ejercicio=Ejercicios.query.filter_by(id=id_ejercicio)
    #alumno=Alumnos.query.filter_by(id=id_alum)    
    print("DESPUES DEL PRINT", id_alum, id_ejercicio)
    
    if request.method =='POST':
        print("despues del post")
        intro_nota = request.form['notaIntroduccion']
        desa_nota = request.form['notaDesarrollo']
        conclu_nota = request.form['notaConclusion']
        
        print(intro_nota, desa_nota, conclu_nota)

        #calif_alumno = PuntajeE.query.filter_by(puntajeE_id = info_calif[0][1].puntajeE_id)

        #db.session.add(calif_alumno.notaI=intro_nota)
        info_calif[0][1].notaI=float(intro_nota)
        info_calif[0][1].notaD=float(desa_nota)
        info_calif[0][1].notaC=float(conclu_nota)

        info_calif[0][1].puntaje_total=(((info_calif[0][1].notaI+info_calif[0][1].notaD+info_calif[0][1].notaC)*70)/100)/10
        print("TOTAL",info_calif[0][1].puntaje_total)
        db.session.commit()
        return redirect(url_for('calificar'))

        #print(info_calif[0][1].notaI,info_calif[0][1].notaD,info_calif[0][1].notaC)
              
    dataTable.append(
            {   'nombreAlumno': info_calif[0][0].nombre,
                'nombreEjercicio': info_calif[0][2].titulo,
                'planteamiento':info_calif[0][2].planteamiento,
                'introduccion':info_calif[0][1].introduccion,
                'desarrollo':info_calif[0][1].desarrollo,
                'conclusion':info_calif[0][1].conclusion,
                'notaI' : info_calif[0][1].notaI,
                'notaD' : info_calif[0][1].notaD,
                'notaC' : info_calif[0][1].notaC
                                    }
        )
    print(dataTable)

    return render_template("ejerciciosADM.html", dataTable = dataTable[0])

@app.route('/evaluar')
def evaluar():
    
    return render_template("evaluar.html")

@app.route('/alumnos/<id>/ver', methods=["get", "post"])
@login_required
def alumnos_ver(id):
    from aplicacion.models import Alumnos, Cursos , PuntajeE
    # Control de permisos
    if not current_user.is_admin():
        abort(404)

    cursos = Cursos.query.all()
    puntaje = PuntajeE.query.filter_by(alu_id=id)
    print(puntaje[0].puntaje_total)
    alu = Alumnos.query.get(id)
    
   
            


    return render_template("alumnos_ver.html",cursos=cursos ,alu=alu, puntaje=puntaje)

@app.route('/actividades/<id>/ver/', defaults={'id_alum': 1}, methods=["GET", "POST"])
@app.route('/actividades/<id>/ver/<id_alum>', methods=["GET", "POST"])
@login_required
def actividades_ver(id, id_alum):

    from aplicacion.models import Actividades, Cursos , PreguntasA, Alumnos, PuntajeA
    

    act = Actividades.query.get(id)
    actividades=Actividades.query.all()

    preguntas = PreguntasA.query.all()
   
    
    if id == '0':
        preguntas = PreguntasA.query.all()
    else:
        id2=int(id)
        preguntas = PreguntasA.query.filter_by(Actividadid=id2)
    actividades = Actividades.query.all()

    cant_preguntas = preguntas.count()
    


    if request.method =='POST':
        calificaciones=[]
        #calificacion= str(request.form['calificacion1'])
        identificador= str(request.form['identificador'])
        cant_preg= str(request.form['cant_preguntas'])

        total_calificacion = 0

        for index in range(0,int(cant_preg)):
            calificaciones.append(str(request.form['calificacion'+str(index+1)]))
            preguntas[index].respuesta = calificaciones[index]
            total_calificacion += int(calificaciones[index])
            print("total",total_calificacion)
            print("cant preg",cant_preg)
            try:
                preguntas[index].cantidad_resp+= 1
            except Exception as e:
                preguntas[index].cantidad_resp = 1
            
            """print("la calificacion emitida es",calificacion)
            print("el id emitido es:", identificador)"""

        
       
        print("El ID de la encuesta es: ", identificador)

        alumno = Alumnos.query.get(id_alum)
        actividades = Actividades.query.get(id)
        print("Actividades", actividades.actividad_resp)
        array_alumnos = []
        for index_alum in actividades.actividad_resp:
            array_alumnos.append(index_alum.id)
            print("A",index_alum)

        print(array_alumnos)

        if alumno.id not in array_alumnos:
            act.actividad_resp.append(alumno)
            punt = PuntajeA(puntaje_total=total_calificacion, alu_id=alumno.id, act_id=id)
            db.session.add(punt)
            db.session.commit()
            print("SE HIZO EL COMMIT")
        else:
            print("Error")
            return render_template("error.html")



        actividad = Actividades.query.all()
        #encuestas[0].encuesta_resp
        print("ENCUESTAS Y ALUMNOS")
        




        return redirect(url_for('inicioAlum', username=alumno.username))
        # acá ingresas a la base de datos

   
    
    return render_template("actividades_ver.html", preguntas=preguntas, act=act, identificador=id, cant_preguntas=cant_preguntas, id_alum=id_alum)

@app.route('/preguntasA/new', methods=["get", "post"])
@login_required
def preguntasA_new():
    from aplicacion.models import PreguntasA , Actividades
    # Control de permisos
    if not current_user.is_admin():
        abort(404)

    form = formPreguntaA()
    actividad = [(a.id, a.nombre) for a in Actividades.query.all()[0:]]
    form.Actividadid.choices = actividad
    if form.validate_on_submit():
        pre = PreguntasA()
        form.populate_obj(pre)
        db.session.add(pre)
        db.session.commit()
        print(pre.nombre)
        return redirect(url_for("actividades"))
    else:
        return render_template("preguntasA_new.html", form=form)

@app.route('/actividades')
def actividades():
    from aplicacion.models import Actividades , PreguntasA
    actividades=Actividades.query.all()
    preguntas=PreguntasA.query.all()
    return render_template("actividades.html", actividades=actividades, preguntas=preguntas)

@app.route('/encuestas/<id>/ver/', defaults={'id_alum': 1}, methods=["GET", "POST"])
@app.route('/encuestas/<id>/ver/<id_alum>', methods=["GET", "POST"])
@login_required
def encuestas_ver(id, id_alum):

    from aplicacion.models import Encuestas, Cursos , Preguntas, Alumnos, Puntaje
    

    enc = Encuestas.query.get(id)
    encuestas=Encuestas.query.all()

    preguntas = Preguntas.query.all()
   
    
    if id == '0':
        preguntas = Preguntas.query.all()
    else:
        id2=int(id)
        preguntas = Preguntas.query.filter_by(Encuestaid=id2)
    encuesta = Encuestas.query.all()

    cant_preguntas = preguntas.count()
    


    if request.method =='POST':
        calificaciones=[]
        #calificacion= str(request.form['calificacion1'])
        identificador= str(request.form['identificador'])
        cant_preg= str(request.form['cant_preguntas'])

        total_calificacion = 0

        for index in range(0,int(cant_preg)):
            calificaciones.append(str(request.form['calificacion'+str(index+1)]))
            preguntas[index].respuesta = calificaciones[index]
            total_calificacion += int(calificaciones[index])
            print("total",total_calificacion)
            print("cant preg",cant_preg)
            try:
                preguntas[index].cantidad_resp+= 1
            except Exception as e:
                preguntas[index].cantidad_resp = 1
            
            """print("la calificacion emitida es",calificacion)
            print("el id emitido es:", identificador)"""

        
       
        print("El ID de la encuesta es: ", identificador)

        alumno = Alumnos.query.get(id_alum)
        encuestas = Encuestas.query.get(id)
        print("encuestas", encuestas.encuesta_resp)
        array_alumnos = []
        for index_alum in encuestas.encuesta_resp:
            array_alumnos.append(index_alum.id)
            print("A",index_alum)

        print(array_alumnos)

        if alumno.id not in array_alumnos:
            enc.encuesta_resp.append(alumno)
            punt = Puntaje(puntaje_total=total_calificacion, alu_id=alumno.id, enc_id=id)
            db.session.add(punt)
            db.session.commit()
            print("SE HIZO EL COMMIT")
        else:
            print("Error")
            return render_template("error2.html")



        encuestas = Encuestas.query.all()
        #encuestas[0].encuesta_resp
        print("ENCUESTAS Y ALUMNOS")
        print(encuestas[0].encuesta_resp)




        return redirect(url_for('inicioAlum', username=alumno.username))
        # acá ingresas a la base de datos

   
    
    return render_template("encuestas_ver.html", preguntas=preguntas, enc=enc, identificador=id, cant_preguntas=cant_preguntas, id_alum=id_alum)


@app.route('/actividades/<id>/verA/', defaults={'id_alum': 1}, methods=["GET", "POST"])
@app.route('/actividades/<id>/verA/<id_alum>', methods=["GET", "POST"])
@login_required
def actividades_verA(id, id_alum):

    from aplicacion.models import Actividades, Cursos , PreguntasA, Alumnos, Puntaje
    
    act = Actividades.query.get(id)
    actividades=Actividades.query.all()
    preguntas = PreguntasA.query.all()
   
    
    if id == '0':
        preguntas = PreguntasA.query.all()
    else:
        id2=int(id)
        preguntas = PreguntasA.query.filter_by(Actividadid=id2)
    actividad = Actividades.query.all()
    cant_preguntas = preguntas.count()
    
    if request.method =='POST':
        calificaciones=[]
        #calificacion= str(request.form['calificacion1'])
        identificador= str(request.form['identificador'])
        cant_preg= str(request.form['cant_preguntas'])

        total_calificacion = 0

        for index in range(0,int(cant_preg)):
            calificaciones.append(str(request.form['calificacion'+str(index+1)]))
            preguntas[index].respuesta = calificaciones[index]
            total_calificacion += int(calificaciones[index])
            print("total",total_calificacion)
            print("cant preg",cant_preg)
            try:
                preguntas[index].cantidad_resp+= 1
            except Exception as e:
                preguntas[index].cantidad_resp = 1
                 
       
        print("El ID de la encuesta es: ", identificador)

        alumno = Alumnos.query.get(id_alum)
        actividades = Actividades.query.get(id)
        print("actividades", actividades.actividad_resp)
        array_alumnos = []
        for index_alum in actividades.actividad_resp:
            array_alumnos.append(index_alum.id)
            print("A",index_alum)

        print(array_alumnos)

        if alumno.id not in array_alumnos:
            act.actividad_resp.append(alumno)
            punt = Puntaje(puntaje_total=total_calificacion/int(cant_preg), alu_id=alumno.id, act_id=id)
            db.session.add(punt)
            db.session.commit()
            print("SE HIZO EL COMMIT")
        else:
            print("Error")
            return render_template("error2.html")

        actividades = Actividades.query.all()
        #encuestas[0].encuesta_resp
        print("Act Y ALUMNOS")
        print(actividades[0].actividad_resp)

        return redirect(url_for('inicioAlum', username=alumno.username))
        # acá ingresas a la base de datos
     
    return render_template("actividades_verA.html", id_actividad=id, preguntas=preguntas, act=act, identificador=id, cant_preguntas=cant_preguntas, id_alum=id_alum)



@app.route('/encuestas/<id>/verA/', defaults={'id_alum': 1}, methods=["GET", "POST"])
@app.route('/encuestas/<id>/verA/<id_alum>', methods=["GET", "POST"])
@login_required
def encuestas_verA(id, id_alum):

    from aplicacion.models import Encuestas, Cursos , Preguntas, Alumnos, Puntaje
    
    enc = Encuestas.query.get(id)
    encuestas=Encuestas.query.all()
    preguntas = Preguntas.query.all()
   
    
    if id == '0':
        preguntas = Preguntas.query.all()
    else:
        id2=int(id)
        preguntas = Preguntas.query.filter_by(Encuestaid=id2)
    encuesta = Encuestas.query.all()
    cant_preguntas = preguntas.count()
    
    if request.method =='POST':
        calificaciones=[]
        #calificacion= str(request.form['calificacion1'])
        identificador= str(request.form['identificador'])
        cant_preg= str(request.form['cant_preguntas'])

        total_calificacion = 0

        for index in range(0,int(cant_preg)):
            calificaciones.append(str(request.form['calificacion'+str(index+1)]))
            preguntas[index].respuesta = calificaciones[index]
            total_calificacion += int(calificaciones[index])
            print("total",total_calificacion)
            print("cant preg",cant_preg)
            try:
                preguntas[index].cantidad_resp+= 1
            except Exception as e:
                preguntas[index].cantidad_resp = 1
                 
       
        print("El ID de la encuesta es: ", identificador)

        alumno = Alumnos.query.get(id_alum)
        encuestas = Encuestas.query.get(id)
        print("encuestas", encuestas.encuesta_resp)
        array_alumnos = []
        for index_alum in encuestas.encuesta_resp:
            array_alumnos.append(index_alum.id)
            print("A",index_alum)

        print(array_alumnos)

        if alumno.id not in array_alumnos:
            enc.encuesta_resp.append(alumno)
            punt = Puntaje(puntaje_total=total_calificacion/int(cant_preg), alu_id=alumno.id, enc_id=id)
            db.session.add(punt)
            db.session.commit()
            print("SE HIZO EL COMMIT")
        else:
            print("Error")
            return render_template("error.html")

        encuestas = Encuestas.query.all()
        #encuestas[0].encuesta_resp
        print("ENCUESTAS Y ALUMNOS")
        print(encuestas[0].encuesta_resp)

        return redirect(url_for('inicioAlum', username=alumno.username))
        # acá ingresas a la base de datos
     
    return render_template("encuestas_verA.html", id_encuesta=id, preguntas=preguntas, enc=enc, identificador=id, cant_preguntas=cant_preguntas, id_alum=id_alum)


@app.route('/errorR')
def errorR():
    return "Error"

@app.route('/preguntas')
def preguntas():
    from aplicacion.models import Preguntas
    preguntas = Preguntas.query.all()
    return render_template("preguntas.html", preguntas=preguntas)


@app.route('/preguntasA')
def preguntasA():
    from aplicacion.models import PreguntasA
    preguntas = PreguntasA.query.all()
    return render_template("preguntasA.html", preguntas=preguntas)

@app.route('/enlazar') 
def enlazar():
    from aplicacion.models import Alumnos, Encuestas , encuesta_alumno, enc_alu
    alumnos = Alumnos.query.all()
    encuestas = Encuestas.quey.all()
    enc = encuesta_alumno(id_alumno=alumnos[0].id, id_encuesta=encuestas[0].id)
    db.session.add(enc)
    db.session.commit()


    return render_template("preguntas.html", preguntas=preguntas)

@app.route('/cursos/new', methods=["get", "post"])
@login_required
def cursos_new():
    
    from aplicacion.models import Cursos , Encuestas
    # Control de permisos
    if not current_user.is_admin():
        abort(404)

    form = formCurso(request.form)
    if form.validate_on_submit():
        cur = Cursos(nombre=form.nombre.data)
        db.session.add(cur)
        db.session.commit()
        return redirect(url_for("cursos"))
    else:
        return render_template("cursos_new.html", form=form)


@app.route('/preguntas/new', methods=["get", "post"])
@login_required
def preguntas_new():
    from aplicacion.models import Preguntas , Encuestas
    # Control de permisos
    if not current_user.is_admin():
        abort(404)

    form = formPregunta()
    encuestas = [(e.id, e.nombre) for e in Encuestas.query.all()[0:]]
    form.Encuestaid.choices = encuestas
    if form.validate_on_submit():
        pre = Preguntas()
        form.populate_obj(pre)
        db.session.add(pre)
        db.session.commit()
        print(pre.nombre)
        return redirect(url_for("encuestas"))
    else:
        return render_template("preguntas_new.html", form=form)

@app.route('/ejercicios/new', methods=["get", "post"])
@login_required
def ejercicios_new():
    from aplicacion.models import Ejercicios, Cursos
    # Control de permisos
    if not current_user.is_admin():
        abort(404)

    form = formEjercicio()
    cursos = [(c.id, c.nombre) for c in Cursos.query.all()[0:]]
    form.Cursoid.choices = cursos
    if form.validate_on_submit():
        eje = Ejercicios()
        form.populate_obj(eje)
        db.session.add(eje)
        db.session.commit()
        return redirect(url_for("ejercicios"))
    else:
        return render_template("ejercicios_new.html", form=form)


@app.route('/encuestas/new', methods=["get", "post"])
@login_required
def encuestas_new():
    from aplicacion.models import Encuestas, Cursos
    # Control de permisos
    if not current_user.is_admin():
        abort(404)

    form = formEncuesta()
    cursos = [(c.id, c.nombre) for c in Cursos.query.all()[0:]]
    form.Cursoid.choices = cursos
    if form.validate_on_submit():
        enc = Encuestas()
        form.populate_obj(enc)
        db.session.add(enc)
        db.session.commit()
        return redirect(url_for("encuestas"))
    else:
        return render_template("encuestas_new.html", form=form)

@app.route('/encuestas/<id>/edit', methods=["get", "post"])
@login_required
def encuestas_edit(id):
    from aplicacion.models import Encuestas, Cursos , Preguntas
    # Control de permisos
    if not current_user.is_admin():
        abort(404)

    enc = Encuestas.query.get(id)
    
    
    
    if enc is None:
        abort(404)
    form = formEncuesta(obj=enc)
    cursos = [(c.id, c.nombre) for c in Cursos.query.all()[0:]]
    form.Cursoid.choices = cursos
    if form.validate_on_submit():
        
      
        form.populate_obj(enc)
        db.session.commit()
        return redirect(url_for("inicio"))
    return render_template("encuestas_new.html", form=form)



@app.route('/preguntas/<id>/edit/<id_encuesta>', methods=["get", "post"])
@login_required
def preguntas_edit(id, id_encuesta):
    from aplicacion.models import Encuestas , Preguntas
    print("id_pregunta: %s - id_encuesta: %s" % (id, id_encuesta))
    # Control de permisos
    if not current_user.is_admin():
        abort(404)

    
    print("imprimir id: ", id)
    preguntas = Preguntas.query.filter_by(Encuestaid=id_encuesta).filter_by(id=id)
    print("idEncuesta", preguntas[0].Encuestaid)
    
    if preguntas is None:
        abort(404)

    if request.method == "POST":
        texto = request.form['nombre_preg']
        print(texto)
        preguntas[0].nombre = texto
        db.session.commit()
    
    # form = formPreguntaE(obj=preguntas)
    # encuestas = [(e.id, e.nombre) for e in Encuestas.query.all()[0:]]
    # form.Encuestaid.choices = encuestas
    # if form.validate_on_submit():
        
      
    #     form.populate_obj(preguntas)
    #     print("antes del commit")
    #     db.session.commit()
        return redirect(url_for("encuestas_verA", id=id_encuesta))
    return render_template("preguntas_edit.html", nombre_pregunta = preguntas[0].nombre)

@app.route('/preguntasA/<id>/edit/<id_actividad>', methods=["get", "post"])
@login_required
def preguntasA_edit(id, id_actividad):
    from aplicacion.models import Actividades , PreguntasA
    print("id_pregunta: %s - id_actividad: %s" % (id, id_actividad))
    # Control de permisos
    if not current_user.is_admin():
        abort(404)

    
    print("imprimir id: ", id)
    preguntas = PreguntasA.query.filter_by(Actividadid=id_actividad).filter_by(id=id)
    print("id_actividad", preguntas[0].Actividadid)
    
    if preguntas is None:
        abort(404)

    if request.method == "POST":
        texto = request.form['nombre_preg']
        print(texto)
        preguntas[0].nombre = texto
        db.session.commit()
    
        return redirect(url_for("actividades_verA", id=id_actividad))
    return render_template("preguntasA_edit.html", nombre_pregunta = preguntas[0].nombre)

@app.route('/archivos/new', methods=["get", "post"])
@login_required
def archivos_new():
    from aplicacion.models import Image, Cursos
    # Control de permisos
    if not current_user.is_admin():
        abort(404)
        
    form = formArchivo()
    cursos = [(c.id, c.nombre) for c in Cursos.query.all()[0:]]
    form.Cursoid.choices = cursos
    if form.validate_on_submit():
        try:
            f = form.photo.data
            nombre_fichero = secure_filename(f.filename)
            f.save(app.root_path + "/static/upload/" + nombre_fichero)
        except:
            nombre_fichero = ""
        arc = Image()
        form.populate_obj(arc)
        arc.image = nombre_fichero
        db.session.add(arc)
        db.session.commit()
        return redirect(url_for("inicio"))
    else:
        return render_template("archivos_new.html", form=form)

@app.route('/ejercicios/<id>/edit', methods=["get", "post"])
@login_required
def ejercicios_edit(id):
    from aplicacion.models import Ejercicios, Cursos 
    # Control de permisos
    if not current_user.is_admin():
        abort(404)

    eje = Ejercicios.query.get(id)
    
  
    if eje is None:
        abort(404)
    form = formEjercicio(obj=eje)
    cursos = [(c.id, c.nombre) for c in Cursos.query.all()[0:]]
    form.Cursoid.choices = cursos
    if form.validate_on_submit():
        
      
        form.populate_obj(eje)
        db.session.commit()
        return redirect(url_for("inicio"))
    return render_template("ejercicios_new.html", form=form)

@app.route('/actividades/new', methods=["get", "post"])
@login_required
def actividades_new():
    from aplicacion.models import Actividades, Cursos
    # Control de permisos
    if not current_user.is_admin():
        abort(404)

    form = formActividad()
    cursos = [(c.id, c.nombre) for c in Cursos.query.all()[0:]]
    form.Cursoid.choices = cursos
    if form.validate_on_submit():
        act = Actividades()
        form.populate_obj(act)
        db.session.add(act)
        db.session.commit()
        return redirect(url_for("actividades"))
        
    else:
        return render_template("actividades_new.html", form=form)

@app.route('/actividades/<id>/edit', methods=["get", "post"])
@login_required
def actividades_edit(id):
    from aplicacion.models import Actividades, Cursos , PreguntasA
    # Control de permisos
    if not current_user.is_admin():
        abort(404)
    
    act = Actividades.query.get(id)
    
    preguntas = PreguntasA.query.all()
    print("El valor del id actual es",id)
    
    if int(preguntas[0].Actividadid) == int(id):
        print("es")
    else:
            print("no es",preguntas[0].Actividadid,id)
    
    if act is None:
        abort(404)
    form = formActividad(obj=act)
    cursos = [(c.id, c.nombre) for c in Cursos.query.all()[0:]]
    form.Cursoid.choices = cursos
    if form.validate_on_submit():
             
        form.populate_obj(act)
        db.session.commit()
        return redirect(url_for("inicio"))
    return render_template("actividades_new.html", form=form)

@app.route('/alumnos/new', methods=["get", "post"])
@login_required
def alumnos_new():
    from aplicacion.models import Alumnos, Cursos
    # Control de permisos
    if not current_user.is_admin():
        abort(404)

    if request.method == "POST":
        texto = request.form['username']
        alumnos=Alumnos.query.all()
        alumnosT=len(alumnos)
        for index in range(0,alumnosT):
            if texto == alumnos[index].username:
                print("encontre que es igual")
                return render_template("existe.html")
         
    form = formAlumno()
    cursos = [(c.id, c.nombre) for c in Cursos.query.all()[0:]]
    form.Cursoid.choices = cursos
    if form.validate_on_submit():
        try:
            f = form.photo.data
            nombre_fichero = secure_filename(f.filename)
            f.save(app.root_path + "/static/upload/" + nombre_fichero)
        except:
            nombre_fichero = ""
        alu = Alumnos()
        form.populate_obj(alu)
        alu.image = nombre_fichero
        db.session.add(alu)
        db.session.commit()
        return redirect(url_for("inicio"))
    else:
        return render_template("alumnos_new.html", form=form)

@app.route('/alumnos/<id>/edit', methods=["get", "post"])
@login_required
def alumnos_edit(id):
    from aplicacion.models import Alumnos, Cursos
     # Control de permisos
    if not current_user.is_admin():
        abort(404)

    alu = Alumnos.query.get(id)
    if alu is None:
        abort(404)
    form = formAlumnoE(obj=alu)
    cursos = [(c.id, c.nombre) for c in Cursos.query.all()[0:]]
    form.Cursoid.choices = cursos
    if form.validate_on_submit():
        
      
        form.populate_obj(alu)
        db.session.commit()
        return redirect(url_for("inicio"))
    return render_template("alumnos_edit.html", form=form)



@app.route('/alumnos/<id>/delete', methods=["get", "post"])
@login_required
def alumnos_delete(id):
    from aplicacion.models import Alumnos , Puntaje , PuntajeA
    # Control de permisos
    if not current_user.is_admin():
        abort(404)
    puntajes= Puntaje.query.filter_by(alu_id=id)
    print("EL ALRGO DE PTS ES",puntajes.count())
    largo=puntajes.count()
    
    puntajesA= PuntajeA.query.filter_by(alu_id=id)
    print("EL ALRGO DE PTS ES",puntajesA.count())
    largo2=puntajesA.count()
    alu = Alumnos.query.get(id)
    if alu is None:
        abort(404)
    form = formSINO()
    if form.validate_on_submit():
        if form.si.data:
            
           
            for index in range(0, largo):
                db.session.delete(puntajesA[index])
                db.session.commit()

            for index in range(0, largo2):
                db.session.delete(puntajesA[index])
                db.session.commit()

        db.session.delete(alu)
        db.session.commit()
        return redirect(url_for("inicio"))
    return render_template("alumnos_delete.html", form=form, alu=alu)

@app.route('/cursos/<id>/edit', methods=["get", "post"])
@login_required
def cursos_edit(id):
    from aplicacion.models import Cursos
    # Control de permisos
    if not current_user.is_admin():
        abort(404)

    print("despues del from")
    cur = Cursos.query.get(id)
    print("despues del get")
    print(cur.nombre)
    if cur is None:
        print("none")
        abort(404)
    form = formCurso(request.form, obj=cur)
    print(form)
    if form.validate_on_submit():
        print(cur.nombre)
        form.populate_obj(cur)
        print(cur.nombre)
        db.session.commit()
        return redirect(url_for("cursos"))

    return render_template("cursos_new.html", form=form)

@app.route('/cursos/<id>/ver', methods=["get", "post"])
@login_required
def cursos_ver(id):
    from aplicacion.models import  Cursos,Alumnos
    

    dataTable = []
    curso=Cursos.query.filter_by(id=id)
    print("curso",curso[0].nombre)
    
    alumnos = Alumnos.query.filter_by(Cursoid=id)
    largoalu=alumnos.count()
    print(largoalu)



    for index in range(0,largoalu):
       
            nombreAux=alumnos[index].nombre
            print(nombreAux)
            

            
            dataTable.append(
                        {   
                            'nombreAlumno': nombreAux,
                                            
                                   }
                    )
        
    

    return render_template("cursos_ver.html",dataTable=dataTable,curso=curso)

@app.route('/cursos/<id>/delete', methods=["get", "post"])
@login_required
def cursos_delete(id):
    from aplicacion.models import Cursos,Alumnos,Encuestas ,Puntaje, PuntajeA, Actividades
    # Control de permisos
    if not current_user.is_admin():
        abort(404)


    print("el largo es")
    alumnos=Alumnos.query.filter_by(Cursoid=id)
    encuestas=Encuestas.query.filter_by(Cursoid=id)
    actividades=Actividades.query.filter_by(Cursoid=id)
    largoalu=alumnos.count()
        
    cur = Cursos.query.get(id)
    if cur is None:
        abort(404)
    form = formSINO()
    if form.validate_on_submit():
        if form.si.data:
            for index in range(0, largoalu):
                print("POR AQUI PASO",index)
                puntajesA= Puntaje.query.filter_by(alu_id=alumnos[index].id)
                cpuntaje=puntajesA.count()
                if cpuntaje>0:
                    db.session.delete(puntajesA[index])
                    db.session.commit()
               
                puntajesAA= PuntajeA.query.filter_by(alu_id=alumnos[index].id)
                cpuntajeA=puntajesAA.count()
                if cpuntajeA>0:
                    db.session.delete(puntajesAA[index])
                    db.session.commit()
            db.session.delete(cur)
            db.session.commit()
        return redirect(url_for("cursos"))
    return render_template("cursos_delete.html", form=form, cur=cur)

@app.route('/actividades/<id>/delete', methods=["get", "post"])
@login_required
def actividades_delete(id):
    from aplicacion.models import Actividades, PuntajeA
    puntajes=PuntajeA.query.filter_by(act_id=id)
    totalpuntajes=puntajes.count()
    print("total de puntajes con este test es ",puntajes.count())
    # Control de permisos
    if not current_user.is_admin():
        abort(404)
  
    print("el id del usuario es ",current_user.id)
    act = Actividades.query.get(id)
    if act is None:
        abort(404)
    form = formSINO()
    if form.validate_on_submit():
        if form.si.data:
            for index in range(0, totalpuntajes):
                print("POR AQUI PASO",index)
                db.session.delete(puntajes[0])
                db.session.commit()
               
            db.session.delete(act)
            db.session.commit()
        return redirect(url_for("actividades"))
    return render_template("actividades_delete.html", form=form, act=act)


@app.route('/ejercicios/<id>/delete', methods=["get", "post"])
@login_required
def ejercicios_delete(id):
    from aplicacion.models import Ejercicios
    # Control de permisos
    if not current_user.is_admin():
        abort(404)
  
    eje = Ejercicios.query.get(id)
    if eje is None:
        abort(404)
    form = formSINO()
    if form.validate_on_submit():
        if form.si.data:
            db.session.delete(eje)
            db.session.commit()
        return redirect(url_for("ejercicios"))
    return render_template("ejercicios_delete.html", form=form, eje=eje)

@app.route('/archivos/<filename>/delete', methods=["get", "post"])
@login_required
def archivos_delete(filename):
    from aplicacion.models import Image 
    

    print("filename",filename)
    arc = Image.query.get(filename)

    print("filename",arc.filename)
    if arc is None:
        abort(404)
    form = formSINO()
    if form.validate_on_submit():
        if form.si.data:
            db.session.delete(arc)
            db.session.commit()
        return redirect(url_for("myfiles"))
    return render_template("archivos_delete.html", form=form, arc=arc)

@app.route('/encuestas/<id>/delete', methods=["get", "post"])
@login_required
def encuestas_delete(id):
    from aplicacion.models import Encuestas ,Puntaje
    puntajes=Puntaje.query.filter_by(enc_id=id)
    totalpuntajes=puntajes.count()
    print("Total de puntajes en esta encuesta",puntajes.count())
    # Control de permisos
    if not current_user.is_admin():
        abort(404)
  
    enc = Encuestas.query.get(id)
    if enc is None:
        abort(404)
    form = formSINO()
    if form.validate_on_submit():
        if form.si.data:
            for index in range(0, totalpuntajes):
                print("POR AQUI PASO",index)
                db.session.delete(puntajes[0])
                db.session.commit()

            db.session.delete(enc)
            db.session.commit()
        return redirect(url_for("encuestas"))
    return render_template("encuestas_delete.html", form=form, enc=enc)

@app.route('/login', methods=['get', 'post'])
def login():
    from aplicacion.models import Alumnos
    # Control de permisos
    if current_user.is_authenticated:
        return redirect(url_for("inicio"))
        
    form = LoginForm()
    if form.validate_on_submit():
        user = Alumnos.query.filter_by(username=form.username.data).first()
        
        if user is not None and user.verify_password(form.password.data):
            login_user(user)
            if user.admin==True:
                print("soy admin")
            else:
                    print("soy normal")
                    
                    return redirect(url_for('inicioAlum', username=user.username))
                    
            print(user)
            return redirect(url_for('inicio'))
        form.username.errors.append("Usuario o contraseña incorrectas.")
    return render_template('login.html', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))

    

@app.route("/registro", methods=["get", "post"])
@login_required
def registro():
    from aplicacion.models import Alumnos
    # Control de permisos
    if current_user.is_authenticated:
        return redirect(url_for("inicio"))

    form = formAlumno()
    if form.validate_on_submit():
        existe_alumno = Alumnos.query.\
            filter_by(username=form.username.data).first()
        if existe_alumno is None:
            user = Alumnos()
            form.populate_obj(user)
            user.admin = False
            db.session.add(user)
            db.session.commit()
            return redirect(url_for("inicio"))
        form.username.errors.append("Nombre de usuario ya existe.")
    return render_template("alumnos_new.html", form=form)


@app.route('/perfil/<username>', methods=["get", "post"])
def perfil(username):
    from aplicacion.models import Alumnos 

    user = Alumnos.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    form = formAlumnoED(request.form, obj=user)
    del form.password
    if form.validate_on_submit():
        form.populate_obj(user)
        db.session.commit()
        return redirect(url_for("inicio"))


    return render_template("usuarios_new.html", form=form, perfil=True)




@app.route('/inicioAA/<username>', methods=["get", "post"])
def inicioAA(username):
    from aplicacion.models import Alumnos , Encuestas , Cursos , Actividades, Ejercicios ,PuntajeE

    """alumnos= Alumnos.query.all()
    actividades= Actividades.query.all()
    ejercicios= Ejercicios.query.all()
    cursos =Cursos.query.all()
    encuestas =Encuestas.query.all()"""
    alum=Alumnos.query.filter_by(username=username)
    cur=Cursos.query.filter_by(id=alum[0].Cursoid)
    encuestasalu=Encuestas.query.filter_by(Cursoid=cur[0].id)
    actividadesalu=Actividades.query.filter_by(Cursoid=cur[0].id)
    ejerciciosalu=Ejercicios.query.filter_by(Cursoid=cur[0].id)

    

    return render_template("inicioAA.html",cur=cur,alum=alum,encuestasalu=encuestasalu,actividadesalu=actividadesalu,ejerciciosalu=ejerciciosalu)


@app.route('/changepassword/<username>', methods=["get", "post"])
@login_required
def changepassword(username):
    from aplicacion.models import Alumnos
    user = Alumnos.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    form = FormChangePassword()
    if form.validate_on_submit():
        form.populate_obj(user)
        db.session.commit()
        return redirect(url_for("inicio"))
    return render_template("changepassword.html", form=form)

@login_manager.user_loader
def load_user(user_id):
    from aplicacion.models import Alumnos
    return Alumnos.query.get(int(user_id))

@app.errorhandler(404)
def page_not_found(error):
    return render_template("error.html", error="Página no encontrada..."), 404

if __name__ == '__main__':
    app.run(debug=True, host="localhost", port=8000)
