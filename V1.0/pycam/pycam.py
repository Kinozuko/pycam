'''
Se importan las librerias necesarias
	cv2 -> Libreria para el manejo y procesamiento de imagenes
	os -> Libreria para la manipulacion del sistema
	MySQLdb -> Libreria para el manejo de la base de datos Mysql
	numpy -> Libreria para el computo cientifico
	datetime -> Libreria para el manejo de formatos de horas y fechas
	werkzeug.security -> Libreria paa la generacion de claves encriptadas (viene integrado con Flask)
	pycam.shh -> Libreria de la conexion SSH
'''

import cv2
import os
import MySQLdb
import numpy as np
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from pycam.ssh import SSHConnection

class PyCam(object):
	
	_tipo_persona = {0 : 'estudiante', 1 : 'padm' , 2 : 'pobrero'}

	_tipo_usuario = {0 : 'adm', 1 : 'gaceta', 2 : 'registro'}

	_initial_sql = [	
	"""create table IF NOT EXISTS persona(
		id integer AUTO_INCREMENT PRIMARY KEY,
		id_tipo integer not null, 
		nombre varchar(50), 
		apellido varchar(50), 
		cedula varchar(10),
		tipo enum('estudiante','padm','pobrero')
	);""",


	"""create table IF NOT EXISTS estudiante(
		id integer AUTO_INCREMENT PRIMARY KEY,
		carrera varchar(50), 
		semestre varchar(50)
	);""",

	"""create table IF NOT EXISTS pobrero(
		id integer AUTO_INCREMENT PRIMARY KEY,
		sueldo decimal(14,2)
	);""",

	"""create table IF NOT EXISTS padm(
		id integer AUTO_INCREMENT PRIMARY KEY,
		costo_hora decimal(14,2)
	);""",

	"""create table IF NOT EXISTS usuarios(
		id integer AUTO_INCREMENT PRIMARY KEY,
		usuario varchar(20),
		clave varchar(120),
		tipo enum('adm','gaceta','registro')
	);""",

	"""create table IF NOT EXISTS registro(
		id integer AUTO_INCREMENT PRIMARY KEY,
		id_persona integer not null, 
		entro bool,
		FOREIGN KEY (id_persona) REFERENCES persona(id)
	);""",

	"""create table IF NOT EXISTS registroinformacion(
		id integer AUTO_INCREMENT PRIMARY KEY,
		id_persona integer not null,
		id_usuario_entrada integer not null,
		id_usuario_salida integer not null,
		fecha_entrada date,
		hora_entrada time,
		fecha_salida date,
		hora_salida time,
		equipo varchar(150),
		FOREIGN KEY (id_persona) REFERENCES persona(id),
		FOREIGN KEY (id_usuario_entrada) REFERENCES usuarios(id),
		FOREIGN KEY (id_usuario_salida) REFERENCES usuarios(id)
	);""",

	"""create table IF NOT EXISTS noregistrado(
		id integer AUTO_INCREMENT PRIMARY KEY,
		id_usuario integer not null,
		id_persona integer not null,
		nombre varchar(50),
		apellido varchar(50),
		cedula varchar(10),
		motivo varchar(100),
		equipo varchar(150),
		fecha_entrada date,
		hora_entrada time,
		fecha_salida date,
		hora_salida time,
		FOREIGN KEY (id_persona) REFERENCES persona(id),
		FOREIGN KEY (id_usuario) REFERENCES usuarios(id)
	);"""]

	face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

	fourcc = cv2.VideoWriter_fourcc(*'XVID')
	face_recognizer = cv2.face.LBPHFaceRecognizer_create()
	database = None

	file_name = str(datetime.datetime.now()).replace("-","").replace(" ","").replace(":","").replace(".","") +".avi"

	# SSH connection data

	host = "192.168.1.143"
	username = "pi"
	pw = "root"

	# Activar camara IP

	'''

	https://stackoverflow.com/questions/49978705/access-ip-camera-in-python-opencv

	http://www.dream-enterprise.com/_wp/python-3-and-opencv-with-an-ip-camera/

	self.video = cv2.VideoCapture('rtsp://IP/1')

	self.video = cv2.VideoCapture('rtsp://username:password@IP/1')

	'''

	#Usar multiples camaras por el mismo BUS

	'''
	https://stackoverflow.com/questions/29664399/capturing-video-from-two-cameras-in-opencv-at-once

	cap0 = cv2.VideoCapture(0)
	cap0.set(3,160)
	cap0.set(4,120)
	cap1 = cv2.VideoCapture(1)
	cap1.set(3,160)
	cap1.set(4,120)
	ret0, frame0 = cap0.read()
	assert ret0 #succeds
	ret1, frame1 = cap1.read()
	assert ret1 #succeds

	'''

	def __init__(self,train = True, usuario = "gaceta1", entrada = 1, IP = False, camera = 0, IP_route=""):
		self.usuario = usuario
		if not IP:
			self.video = cv2.VideoCapture(camera)
		else:
			self.video = cv2.VideoCapture(IP_route)
		self.out = cv2.VideoWriter(self.file_name,self.fourcc,20.0,(640,480))
		# Configuracion para localhost
		#self.database = MySQLdb.connect(host="localhost",port=3306,user="root",passwd="",db="initial")
		# Configuracion para el Raspberry
		#self.database = MySQLdb.connect(host="192.168.1.143",port=3306,user="user",passwd="toor",db="initial")
		# Configuracion para el Raspberry usando un switch
		self.database = MySQLdb.connect(host="169.254.25.163",port=3306,user="user",passwd="toor",db="initial")
		self.entrada = entrada
		if train == True:
			self.face_recognizer.read("trainer/trainer.yml")

	def __del__(self):
		self.video.release()
		self.out.release()
		self.database.close()
		# Cuando se requiere que el video se almacene en el servidor
		'''
		ssh = SSHConnection(self.host,self.username,self.pw)
		ssh.put("C:\\Users\\victo\\Desktop\\TESIS\\PyCam\\V1.0\\"+self.file_name,"/home/pi/PyCam/videos/"+self.file_name)
		ssh.close()
		'''

	def get_frame(self):
		# Se accede al curso para trabajar con la base de datos
		cursor = self.database.cursor()
		# Se lee los frames del video
		success, image = self.video.read()
		# Si se lee un frame satisfactorio
		if success:
			# Se convierte el frame en formato Gray
			gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
			# Se detecta rostros en el frame
			faces = self.face_cascade.detectMultiScale(gray,1.2,10)
			# Se analizan todos los rostros encontrados
			for (x,y,w,h) in faces:
				cv2.rectangle(image,(x,y),(x+w,y+h),(0,255,0),3)
				# Se realiza la prediccion de los rostros utilizando el reconocedor
				ids,conf = self.face_recognizer.predict(gray[y:y+w,x:x+h])
				# Se realiza el query para buscar el nomrbe y apellido de todas las predicciones
				cursor.execute("SELECT id,nombre,apellido FROM persona WHERE id = '%s';",(ids,))
				# se traabjan con los valores resultantes del query
				result = cursor.fetchall()
				id_persona = result[0][0]
				nombre = result[0][1]
				apellido = result[0][2]
				# Se establece el parametro de confiabilida
				if conf < 55:
					entro, salio = 0,0
					# Se realiza un query para obtener la informacion de si la persona ha entrado o no
					sql_response = cursor.execute("SELECT id,id_persona,entro FROM registro WHERE id_persona = '%s' ORDER BY id  DESC;", (id_persona, ))
					# Se trabaja con el primer dato resultante del query
					registro = cursor.fetchone()
					# Se genera la fecha y hora actual 
					now = datetime.datetime.now()
					# Se separa la fecha y la hora en dos variables distintas
					date = now.strftime("%Y-%m-%d")
					time = now.strftime("%H:%M:%S")
					# Se realiza un query para la extraccion de los datos del usuario
					cursor.execute("SELECT id FROM usuarios WHERE usuario = %s;", (self.usuario,))
					id_usuario = cursor.fetchone()[0]
					# Si la camara actua como entrada
					if self.entrada == 1:
						# Si el qury para obtener la informacion no da resultados se crean los nuevos registros
						if sql_response == 0:
							cursor.execute("INSERT INTO registroinformacion (id_persona,id_usuario_entrada,id_usuario_salida,fecha_entrada,hora_entrada) VALUES (%s,%s,%s,%s,%s);",(id_persona,id_usuario,id_usuario,date,time))
							cursor.execute("INSERT INTO registro (id_persona,entro) VALUES (%s, %s);",(id_persona,True))
						# Si el qury para obtener la informacion  da resultados se verifica el ultimo ingreso que tuvo la persona
						elif sql_response == 1:
							id_registro , entro = registro[0], registro[2]
							# Query para obtener la informacion del ultimo registro de la persona
							cursor.execute("SELECT id,fecha_salida,hora_salida FROM registroinformacion WHERE id_persona ORDER BY id DESC")
							registro_informacion = cursor.fetchone()
							id_registroinformacion = registro_informacion[0]
							# Se verifica si la persona no haya entrado anteriormente sin una posterior salida, en caso de no ser asi se crean nuevos registros
							if registro_informacion[1] != None and registro_informacion[2] != None and entro == 0:
								cursor.execute("INSERT INTO registroinformacion (id_persona,id_usuario_entrada,id_usuario_salida,fecha_entrada,hora_entrada) VALUES (%s,%s,%s,%s,%s);",(id_persona,id_usuario,id_usuario,date,time))
								cursor.execute("UPDATE registro SET entro = %s WHERE id =  %s and id_persona = %s;",(True,id_registro,id_persona))
						self.database.commit()
					#Si la camara actua como salida
					elif self.entrada == 0:
						# Si el qury para obtener la informacion  da resultados se actualiza el ultimo registro
						if sql_response == 1:
							id_registro , entro  = registro[0] , registro [2] 
							# Si la persona actualmente ya ingreso al sistema se actualizan los registros con la salida
							if entro == 1:
								# Se realiza un query para obtener el ultimo registro de la persona
								cursor.execute("SELECT * FROM registroinformacion WHERE id_persona = %s ORDER BY id DESC",(id_persona,))
								registro_informacion = cursor.fetchone();
								id_registroinformacion = registro_informacion[0]
								# Se realiza un query para actualizar la informacion del registro y del registro de control
								cursor.execute("UPDATE registroinformacion SET id_usuario_salida = %s, fecha_salida = %s, hora_salida = %s WHERE id = %s;",(id_usuario,date,time,id_registroinformacion))
								cursor.execute("UPDATE registro SET entro = %s WHERE id =  %s and id_persona = %s;",(False,id_registro,id_persona))
								self.database.commit()
					else:
						# En caso de que la camara no sea ni de entrada ni salida no se realiza ninguna accion
						pass
					# Se modifica la imagen colocandole el nombre y apellido de la prediccion a la respectiva persona
					cv2.putText(image,nombre+ " " + apellido,(x+2,y+h-5),cv2.FONT_HERSHEY_SIMPLEX,1,(155,255,0),2)
				else:
					# En caso de no haber una prediccion se indica que la persona es No registrada
					cv2.putText(image,'No Registrado',(x+2,y+h-5),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2)
			ret,jpeg = cv2.imencode('.jpg',image)
			self.out.write(image)
			return jpeg.tobytes(), image

	def create_database(host = "192.168.1.143",username ="user", password = "toor", dbname = 'initial', sql = _initial_sql):
		db = MySQLdb.connect(host=host,port=3306,user=username,passwd=password)
		cursor = db.cursor()
		cursor.execute("create database IF NOT EXISTS "+ dbname +" CHARACTER SET utf8 COLLATE utf8_general_ci;")
		db.select_db(dbname)
		for query in sql:
			cursor.execute(query)
			db.commit()
		db.close()

	def connect_database(self,host,username,password,dbname):
		self.database = MySQLdb.connect(host,username,password,dbname)

	def close_database(self):
		self.database.close()

	def record_face(self,nombre, apellido, cedula,tipo,carrera="",semestre="",sueldo=0.00,costo_hora=0.00):
		#ssh = SSHConnection(self.host,self.username,self.pw)

		# Cuando se necesita trabajar por ssh 

		# ssh.create_folder("/home/pi/PyCam/fotos")
		
		# Cuando se necesita trabajar de manera local

		# Se verifica si el directoria de los positivos de entrenamiento existe, si no existe se crea

		if not os.path.exists('./fotos'):
			os.makedirs('./fotos')
		
		cursor = self.database.cursor()

		if tipo==0:
			cursor.execute('INSERT INTO estudiante (carrera,semestre) VALUES (%s,%s);',(carrera,semestre))
		elif tipo==1:
			cursor.execute('INSERT INTO padm (costo_hora) VALUES (%s);',(costo_hora,))
		elif tipo==2:
			cursor.execute('INSERT INTO pobrero (sueldo) VALUES (%s);',(sueldo,))

		uid = cursor.lastrowid

		cursor.execute('INSERT INTO persona (id_tipo,nombre,apellido,cedula,tipo) VALUES (%s,%s,%s,%s,%s);',
						(uid,nombre,apellido,cedula,self._tipo_persona[tipo]))

		uid = cursor.lastrowid

		sampleNum = 0
		# Cuando se necesita trabajar por ssh

		# ssh.create_folder("/home/pi/PyCam/fotos/P"+str(uid))

		# Cuando se necesita trabajar de manera local

		if not os.path.exists('.fotros/P'+str(uid)):
			os.makedirs('./fotos/P'+str(uid))

		while sampleNum<200:
			success, image = self.video.read()

			if success:
				gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
				faces = self.face_cascade.detectMultiScale(gray,1.2,10)
				for (x,y,w,h) in faces:
					sampleNum = sampleNum + 1
					# Cuando se trabaja de manera local

					cv2.imwrite("fotos/P"+str(uid)+"/face."+str(sampleNum)+".jpg",gray[y:y+h,x:x+w])
					
					# Cuando se requiere trabajar por ssh
					'''
					cv2.imwrite("face."+str(sampleNum)+".jpg",gray[y:y+h,x:x+w])
					ssh.put("C:\\Users\\victo\\Desktop\\TESIS\\PyCam\\V1.0\\face."+str(sampleNum)+".jpg","/home/pi/PyCam/fotos/P"+str(uid)+"/face."+str(sampleNum)+".jpg")
					os.remove("face."+str(sampleNum)+".jpg")
					'''
					cv2.rectangle(image,(x,y),(x+w,y+h),(255,0,0),2)
				cv2.imshow("img",image)
			cv2.waitKey(1)
		self.database.commit()

	def generate_seed_users(self):
		cursor = self.database.cursor()
		# Se realizan todos los query para la creacion de usuarios perdeterminados y persona ficticia
		cursor.execute('INSERT INTO usuarios (usuario,tipo,clave) VALUES ("administrador","adm",%s);',(generate_password_hash("1234"),))
		cursor.execute('INSERT INTO usuarios (usuario,tipo,clave) VALUES ("vigilancia1","gaceta",%s);',(generate_password_hash("1234"),))
		cursor.execute('INSERT INTO usuarios (usuario,tipo,clave) VALUES ("vigilancia2","gaceta",%s);',(generate_password_hash("1234"),))
		cursor.execute('INSERT INTO usuarios (usuario,tipo,clave) VALUES ("registro","registro",%s);',(generate_password_hash("1234"),))
		cursor.execute('INSERT INTO estudiante (carrera,semestre) VALUES ("","");')
		cursor.execute('INSERT INTO padm (costo_hora) VALUES (0);')
		cursor.execute('INSERT INTO pobrero (sueldo) VALUES (0);')
		cursor.execute('INSERT INTO persona (id_tipo,nombre,apellido,cedula,tipo) VALUES (1,"","","","estudiante");')
		self.database.commit()

	def detect_face(img):
		gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
		face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
		faces = face_cascade.detectMultiScale(gray,1.2,10)
		if len(faces)==0:
			return None,None
		(x,y,w,h) = faces[0]

		return gray[y:y+w,x:x+h],faces[0]

	def train_data():
		faces , labels = [] , []

		# se listan todos los directorios de la ruta de las imagenes

		dirs = os.listdir("./fotos")

		# Se iteran a traves de todas las rutas
		for dir_name in dirs:
			# Si el nombre del directorio no comienza ocn P no se realiza nada
			if not dir_name.startswith("P"):
				continue
			# Se modifica el nombre del directorio para extraer la ID de la persona
			label = int(dir_name.replace("P", ""))
			# Se crea la ruta del directorio de la persona
			subject_dir_path = "./fotos/"+dir_name
			# Se listan todos los directorios de la ruta del directorio de la persona
			subject_images_names = os.listdir(subject_dir_path)
			# Se iteran todas las rutas de las imagenes
			for image_name in subject_images_names:
				# Se hace caso omiso de todos los archivos ocultos dentro del directorio
				if image_name.startswith("."):
					continue
				# Se genera la ruta de la imagen
				image_path = subject_dir_path+"/"+image_name
				# Se lee la imagen
				image = cv2.imread(image_path)
				# Se detectan los rostros de la imagen
				face, rect = PyCam.detect_face(image)
				# En caso de encontrar las agrega a las listas de rostros e ids
				if face is not None:
					faces.append(face)
					labels.append(label)
		# Se crea el reconocedor
		face_recognizer = cv2.face.LBPHFaceRecognizer_create()
		# Se entrena el reconocedor con las listas de rostros e ids
		face_recognizer.train(faces,np.array(labels))
		# Si no existe la carpeta para el archivo de entrenamiento se crea
		if not os.path.exists('./trainer'):
			os.makedirs('./trainer')
		# Se guarda el archivo de entrenamiento del reconocedor
		face_recognizer.save("trainer/trainer.yml")

		# Cuando se trabaja por SSH
		'''
		host = "192.168.1.101"
		username = victo
		pw = victor123456

		ssh = SSHConnection(host,username,pw)
		ssh.put("/home/pi/PyCam/trainer/trainer.yml","C:\\Users\\victo\\Desktop\\TESIS\\PyCam\\V1.0\\trainer\\trainer.yml")
		print("Reconocedor entrenado....")
		'''