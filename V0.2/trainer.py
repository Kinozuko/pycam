'''
	Se realizan las importaciones necesarias
	os -> Libreria para la manipulacion del sistema
	cv2 -> Libreria para el manejo y procesamiento de imagenes
	numpy -> Libreria para el computo cientifica
	PIL -> Libreria de imagenes para python
'''
import os
import cv2
import numpy as np
from PIL import Image

# Se crea el reconocedor utilizando el algoritmo LBPH
recognizer = cv2.face.LBPHFaceRecognizer_create()
# Nombre del directoria donde se encuentran los positivos con los cuales se entrenara
path = 'dataset'

# Se verifica si no existe una carpeta para el archivo de entrenamiento, en caso de no existir se crea
if not os.path.exists('./recognizer'):
	os.makedirs('./recognizer')

'''
	Funcion que crea la asociacion de los positivos con el id de la persona
	path -> ruta donde se encuentran los positivos de entrenamiento
	Retorna -> Un array tipo numpy de IDs y una lista de los positivos
'''
def getImagesWithId(path):
	# Se listan todas las rutas de las imagenes a utilizar
	imagePaths = [os.path.join(path,f) for f in os.listdir(path)]
	'''
		Se crean dos listas con las cuales se trabajaran
		faces -> Lista que almacenara los rostros
		IDs -> Lista que almacenara los id de las personas
	'''
	faces = []
	IDs = []
	# Se recorre cada ruta en imagesPahs
	for imagePath in imagePaths:
		# Se toma la imagen de la ruta selecciona para ser convertida en formato Gray
		faceImg = Image.open(imagePath).convert('L')
		# Se crea un array con la libreria numpy para relacionar las imagenes
		faceNp = np.array(faceImg,'uint8')
		# Utilizando la ruta se selecciona el ID correspondiente a los positivos
		ID = int(os.path.split(imagePath)[-1].split('.')[1])
		# Se almacena los valores en la lista faces
		faces.append(faceNp)
		# Se almacena los valores en la lista IDs
		IDs.append(ID)
		cv2.imshow("training",faceNp)
		cv2.waitKey(10)
	return np.array(IDs),faces

# Se relacionan todos los positivos con su respectivo ID
Ids,faces = getImagesWithId(path)
# Se entrena el reconocedor con los ID y positivos obtenidos anteriormente
recognizer.train(faces,Ids)
# Se guarda el archivo de entrenamiento para futuros usos
recognizer.save('recognizer/trainingData.yml')
cv2.destroyAllWindows()

