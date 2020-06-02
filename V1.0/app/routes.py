from app import app, mysql
from flask import Flask, Response, render_template, flash, redirect, session, url_for
from pycam.pycam import PyCam
from app.forms import LoginForm, UserRegister, StudentRegister, PersonalAdmRegister , PersonalRegister, AddItem, Guest, DateForm, GuestCheck
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import cv2
import socket

_tipo_usuario = {'adm' : 'Adiministrador',  'gaceta' : 'Vigilancia', 'registro' : 'Registro'}
_carrera = {'ie':'Ing. Electronica','iet':'Ing. en Telecomunicaciones'}

def gen(camera):
    while True:
        frame, image = camera.get_frame()
        cv2.imshow('Cam 1', image)
        k = cv2.waitKey(30) & 0xff
        if k == 27:
        	break
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed.mjpg')
def video_feed():
	if not session.get('is_aunthenticate'):
		return redirect('/')
	#return Response(gen(PyCam(True,session.get('user_name'),0,True,0,"rtsp://admin:123@127.0.0.1:3454/Media/Live/Normal?camera=C_1&streamindex=1")),mimetype='multipart/x-mixed-replace; boundary=frame')
	return Response(gen(PyCam(True,session.get('user_name'),0)),mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed_2.mjpg')
def video_feed_2():
	if not session.get('is_aunthenticate'):
		return redirect('/')
	return Response(gen(PyCam(True,session.get('user_name'),1)),mimetype='multipart/x-mixed-replace; boundary=frame')
	#return Response(gen(PyCam(True,session.get('user_name'),1,True,0,"rtsp://admin:123@127.0.0.1:3454/Media/Live/Normal?camera=C_2&streamindex=1")),mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/',methods=['GET','POST'])
def login():
	cursor = mysql.connection.cursor()
	form = LoginForm()
	if session.get('is_aunthenticate'):
		usuario  = session.get('user_type')
		if usuario == 'Adiministrador':
			return redirect('/view_users')
		elif usuario == 'Vigilancia':
			return redirect('/index')
		else:
			return redirect('/view_students')
	if form.validate_on_submit():
		_sql_response = cursor.execute("SELECT * FROM usuarios WHERE usuario = %s",[form.username.data,])
		if _sql_response:
			usuario = cursor.fetchone()
			if check_password_hash(usuario[2],form.password.data):
				session['is_aunthenticate'] = True
				session['user_id'] = usuario[0]
				session['user_name'] = usuario[1]
				session['user_type'] = _tipo_usuario[usuario[3]]
				#flash('Bienvenido '+str(usuario[3]))
				if usuario[3] == 'adm':
					return redirect('/view_users')
				elif usuario[3] == 'gaceta':
					return redirect('/index')
				else:
					return redirect('/view_students')
			else:
				flash('Clave invalida')
		else:
			flash('Usuario '+str(form.username.data)+ ' no registrado')
	return render_template('login.html',form=form)


@app.route('/logout')
def logout():
	if session.get('is_aunthenticate'):
		session['is_aunthenticate'] = False
		session['user_id'] = None
		session['user_type'] = None
		session['use_name'] = None
	return redirect('/')

@app.route('/index',methods=['GET','POST'])
def index():
	if not session.get('is_aunthenticate'):
		return redirect('/')
	form = DateForm()
	nombre = session.get('user_type')
	cursor = mysql.connection.cursor()
	date = datetime.now().strftime("%Y-%m-%d")
	if form.validate_on_submit():
		date = form.fecha.data
	cursor.execute("SELECT p.cedula,p.nombre,p.apellido,u1.usuario,u2.usuario,ri.hora_entrada,ri.hora_salida,ri.equipo FROM registroinformacion AS ri JOIN persona AS p ON ri.id_persona = p.id JOIN usuarios AS u1 ON ri.id_usuario_entrada = u1.id JOIN usuarios AS u2 on ri.id_usuario_salida = u2.id WHERE ri.fecha_entrada = %s;",[date,])
	history = cursor.fetchall()
	return render_template('index.html',user=nombre,history = history, date = date, form = form)

@app.route('/user_register',methods=['GET','POST'])
def user_register():
	form = UserRegister()
	cursor = mysql.connection.cursor()
	if not session.get('is_aunthenticate'):
		return redirect('/')
	if form.validate_on_submit():
		_sql_response = cursor.execute("SELECT id FROM usuarios WHERE usuario = %s",[form.usuario.data,])
		if _sql_response:
			flash('El usuario '+str(form.usuario.data)+' ya se encuentra registrado')
		else:
			if str(form.password.data) == str(form.confirm_password.data):
				password = generate_password_hash(form.password.data)
				cursor.execute('INSERT INTO usuarios (usuario,tipo,clave) VALUES (%s,%s,%s);',[form.usuario.data,form.tipo.data,password,])
				mysql.connection.commit()
				flash('Usuario Registrado Satisfactoriamente')
				return redirect(url_for('user_register'))
			else:
				flash('Las claves no coinciden')
	return render_template('user_register.html',form = form)

@app.route('/student_register',methods=['GET','POST'])
def student_register():
	form = StudentRegister()
	if not session.get('is_aunthenticate'):
		return redirect('/')
	if form.validate_on_submit():
		cursor = mysql.connection.cursor()
		_sql_response = cursor.execute("SELECT id FROM persona WHERE cedula = %s",[form.cedula.data,])
		if _sql_response:
			flash('Ya existe un estudiante con la cedula '+str(form.cedula.data))
		else:
			cam =PyCam(False)
			cam.record_face(str(form.nombre.data),str(form.apellido.data),str(form.cedula.data),0,_carrera[form.carrera.data],str(form.semestre.data))
			flash('Estudiante registrado')
			del cam
			return redirect(url_for('student_register'))
	return render_template('student_register.html',form = form)

@app.route('/personal_adm_register',methods=['GET','POST'])
def personal_adm_register():
	form = PersonalAdmRegister()
	if not session.get('is_aunthenticate'):
		return redirect('/')
	if form.validate_on_submit():
		cursor = mysql.connection.cursor()
		_sql_response = cursor.execute("SELECT id FROM persona WHERE cedula = %s",[form.cedula.data,])
		if _sql_response:
			flash('Ya existe un personal con con la cedula ' + str(form.cedula.data))
		else:
			cam = PyCam(False)
			cam.record_face(form.nombre.data,form.apellido.data,form.cedula.data,1,"","",0,form.costo_hora.data)
			flash("Personal agregado")
			del cam
			return redirect(url_for('personal_adm_register'))
	return render_template('personal_adm_register.html',form=form)

@app.route('/personal_register',methods=['GET','POST'])
def personal_register():
	form = PersonalRegister()
	if not session.get('is_aunthenticate'):
		return redirect('/')
	if form.validate_on_submit():
		cursor = mysql.connection.cursor()
		_sql_response = cursor.execute("SELECT id FROM persona WHERE cedula = %s",[form.cedula.data,])
		if _sql_response:
			flash('Ya existe un personal con con la cedula ' + str(form.cedula.data))
		else:
			cam = PyCam(False)
			cam.record_face(form.nombre.data,form.apellido.data,form.cedula.data,2,"","",form.sueldo.data,0)
			flash("Personal agregado")
			del cam
			return redirect(url_for('personal_register'))
	return render_template('personal_register.html',form=form)

@app.route('/add_item',methods=['GET','POST'])
def add_item():
	form = AddItem()
	if not session.get('is_aunthenticate'):
		return redirect('/')
	if form.validate_on_submit():
		cursor = mysql.connection.cursor()
		_sql_response = cursor.execute("SELECT id FROM persona WHERE cedula = %s",[form.cedula.data,])
		if _sql_response:
			id_persona = cursor.fetchone()
			_sql_response_register = cursor.execute("SELECT entro FROM registro WHERE id_persona = %s",[id_persona,])
			if _sql_response_register and cursor.fetchone():
				cursor.execute("SELECT id FROM registroinformacion WHERE id_persona = %s ORDER BY id DESC",[id_persona,] )
				cursor.execute("UPDATE registroinformacion SET equipo = %s WHERE id = %s;",(form.equipo.data,cursor.fetchone()))
				mysql.connection.commit()
				flash("Se han registrado los equipos")
				return redirect(url_for('add_item'))
			else:
				flash('La persona no ha ingresado a las instalaciones')
		else:
			flash('La persona no se encuentra registrada')
	return render_template('add_item.html',form=form)

@app.route('/guest',methods=['GET','POST'])
def guest():
	form = Guest()
	if not session.get('is_aunthenticate'):
		return redirect('/')
	if form.validate_on_submit():
		date = datetime.now().strftime("%Y-%m-%d")
		time = datetime.now().strftime("%H:%M:%S")
		cursor = mysql.connection.cursor()
		if form.cedula_persona.data == "":
			id_persona = 1
		else:
			_sql_response = cursor.execute("SELECT id FROM persona WHERE cedula = %s",[form.cedula_persona.data,])
			if _sql_response:
				id_persona = cursor.fetchone()[0]
			else:
				flash('El usuario que otorga permiso no se encuentra registrado')
				return render_template('guest.html',form=form)
		cursor.execute("INSERT INTO noregistrado(id_usuario,id_persona,nombre,apellido,cedula,motivo,equipo,fecha_entrada,hora_entrada) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s);",[session.get('user_id'),id_persona,form.nombre.data,form.apellido.data,form.cedula.data,form.motivo.data,form.equipo.data,date,time])
		mysql.connection.commit()
		flash("Invitado registrado")
		return redirect(url_for('guest'))
	return render_template('guest.html',form=form)


@app.route('/view_guest',methods=['GET','POST'])
def view_guest():
	if not session.get('is_aunthenticate'):
		return redirect('/')
	form = DateForm()
	nombre = session.get('user_type')
	cursor = mysql.connection.cursor()
	date = datetime.now().strftime("%Y-%m-%d")
	if form.validate_on_submit():
		date = form.fecha.data
	cursor.execute("SELECT  nr.cedula, nr.nombre, nr.apellido, nr.motivo, nr.equipo, u.usuario, p.cedula, p.nombre, p.apellido, nr.hora_entrada, nr.hora_salida, nr.fecha_salida FROM noregistrado AS nr JOIN usuarios AS u ON nr.id_usuario = u.id JOIN persona AS p ON nr.id_persona = p.id WHERE nr.fecha_entrada = %s;",[date,])
	history = cursor.fetchall()
	# select p.nombre, p.apellido, p.cedula,  u1.usuario as Entrada, u2.usuario as Salida, ri.fecha_entrada, ri.hora_entrada, ri.fecha_salida, ri.hora_salida, ri.equipo  from registroinformacion as ri join persona as p on ri.id_persona = p.id join usuarios as u1  on ri.id_usuario_entrada = u1.id join usuarios as u2 on ri.id_usuario_salida = u2.id;
	return render_template('view_guest.html',user=nombre,history = history, date = date,form = form)

@app.route('/view_students')
def view_students():
	if not session.get('is_aunthenticate'):
		return redirect('/')
	nombre = session.get('user_type')
	cursor = mysql.connection.cursor()
	cursor.execute("SELECT p.cedula, p.nombre, p.apellido, e.carrera, e.semestre FROM persona AS p JOIN estudiante AS e ON p.id_tipo = e.id where tipo = 'estudiante' and p.id != 1;")
	history = cursor.fetchall()
	return render_template('view_students.html',user=nombre, history = history)

@app.route('/view_padm')
def view_padm():
	if not session.get('is_aunthenticate'):
		return redirect('/')
	nombre = session.get('user_type')
	cursor = mysql.connection.cursor()
	cursor.execute("SELECT p.cedula, p.nombre, p.apellido, a.costo_hora FROM persona AS p JOIN padm AS a ON p.id_tipo = a.id where tipo = 'padm';")
	history = cursor.fetchall()
	return render_template('view_padm.html',user=nombre, history = history)

@app.route('/view_pobrero')
def view_pobrero():
	if not session.get('is_aunthenticate'):
		return redirect('/')
	nombre = session.get('user_type')
	cursor = mysql.connection.cursor()
	cursor.execute("SELECT p.cedula, p.nombre, p.apellido, o.sueldo FROM persona AS p JOIN pobrero AS o ON p.id_tipo = o.id where tipo = 'pobrero';")
	history = cursor.fetchall()
	return render_template('view_pobrero.html',user=nombre, history = history)

@app.route('/view_users')
def view_users():
	if not session.get('is_aunthenticate'):
		return redirect('/')
	nombre = session.get('user_type')
	cursor = mysql.connection.cursor()
	cursor.execute("SELECT usuario, tipo FROM usuarios;")
	history = cursor.fetchall()
	return render_template('view_users.html',user=nombre,history=history,tipo = _tipo_usuario)

@app.route('/train')
def train():
	if not session.get('is_aunthenticate'):
		return redirect('/')
	PyCam.train_data()
	flash('Archivo de entrenador creado y transferido')
	return redirect('/')

@app.route('/check_guest',methods=['GET','POST'])
def check_guest():
	if not session.get('is_aunthenticate'):
		return redirect('/')
	form = GuestCheck()
	nombre = session.get('user_type')
	cursor = mysql.connection.cursor()
	date = datetime.now().strftime("%Y-%m-%d")
	time = datetime.now().strftime("%H:%M:%S")
	if form.validate_on_submit():
		_sql_response = cursor.execute("SELECT id,fecha_salida, hora_salida FROM noregistrado WHERE cedula = %s ORDER BY id DESC;",(form.cedula.data,))
		if _sql_response:
			guest = cursor.fetchone()
			if guest[1]==None:
				cursor.execute("UPDATE noregistrado SET fecha_salida = %s, hora_salida = %s WHERE id = %s;",(date,time,guest[0]))
				mysql.connection.commit()
				flash("Salida del invitado registrado")
				return redirect(url_for('check_guest'))
			else:
				flash("Ya el invitadoo se le ha registrado la salida")
				return render_template('check_guest.html',form=form)
		else:
			flash('El invitado aun no ha sido registrado')
			return render_template('check_guest.html',form=form)
	return render_template('check_guest.html',form = form)
