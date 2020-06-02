'''
	Se realizan las importaciones necesarias
	os -> Libreria para la manipulacion del sistema
	cv2 -> Libreria para el manejo y procesamiento de imagenes
	numpy -> Libreria para el computo cientifica
	sqlite3 -> Libreria para manipular bases de datos tipo sqlite
'''
import cv2
import numpy as np
import sqlite3
import os

# Se realiza la conexion con la base de datos y se crea el cursor de la misma
conn = sqlite3.connect('database.db')
c = conn.cursor()

# Nombre del archivo de entrenamiento a utilizar
fname = "recognizer/trainingData.yml"

# Verifica si el archivo de entrenamiento existe si no manda una advertencia
if not os.path.isfile(fname):
	print("Entrene la data primero")
	exit(0)

# Se selecciona el clasificador de rostros frontales haarcascade
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
# Se inicia la video captura de la camara web
cap = cv2.VideoCapture(0)
# Se crea el reconocedor LBPH
recognizer = cv2.face.LBPHFaceRecognizer_create()
# Se entrena el reconocendor con el archivo de entrenamiento
recognizer.read(fname)

# Se inicia el reconocimiento facial en vivo
while True:
	'''
		Se lee un frame del video captura
		ret -> Respuesta de la lectura True si fue satisfactoria de lo contrario False
		img -> Imagen con la que se trabajara
	'''
	ret,img = cap.read()
	# Se transforma la imagen original a formato Gray
	gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
	# Utilizando el clasificador se detectan rostros
	faces = face_cascade.detectMultiScale(gray,1.3,5)
	# Para todos los rostros detectados 
	for (x,y,w,h) in faces:
		# Se crea un rectangulo en el rostro de la persona que fue detectada
		cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),3)
		'''
			Se realiza la prediccion del rostro detectado utilizando el reconocedor
			ids -> Id de las personas que fueron reconocidas
			conf -> Confianza de la prediccion (entre menor sea el numero mas eficiente es)
		'''
		ids,conf = recognizer.predict(gray[y:y+h,x:x+w])
		# Se ejecuta el query en la base de datos para selecciona el nombre de las personas que fueron reconocidas
		c.execute("select nombre from persona where id = (?);",(ids,))
		# Se toman todas las respuestas dadas por el query
		result = c.fetchall()
		# Se selecciona el nombre de la persona que fue reconocida
		name = result[0][0]
		# Se verifica si la confiabilidad es menor a 50
		if conf < 50:
			# En caso de ser se le coloca el nombre de la persona en la imagen
			cv2.putText(img,name,(x+2,y+h-5),cv2.FONT_HERSHEY_SIMPLEX,1,(155,255,0),2)
		else:
			# En caos de que no se coloca que la persona no ha sido reconocida
			cv2.putText(img,'No Registrado',(x+2,y+h-5),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2)
	cv2.imshow('Reconocimiento Facial',img)
	k =cv2.waitKey(30) & 0xff
	if k == 27:
		break
cap.release()
cv2.destroyAllWindows()
