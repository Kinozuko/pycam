#Se importa la libreria de opencv
import cv2

'''
Funcion que convierte una imagen en BGR a RGB
arg -> img <- Imagen a convertir
function convertToRGB(img)
return img convertida a RGB
'''

def convertToRGB(img):
	return cv2.cvtColor(img,cv2.COLOR_BGR2RGB)

'''
Funcion que convierte una imagen en BGR a Gray
arg -> img <- Imagen a convertir
function convertToGrey(img)
return img convertida a Gray
'''
def convertToGray(img):
	return cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

'''
Funcion que detecta rostros en una imagen determinada
f_cascade -> clasificador a utilizar
colored_img -> Imagen con la que se trabajara
scaleFactor -> Factor de escala para la deteccion, por defecto tendra el valor de 1.1
retorna -> Copia de la imagen con las detecciones realizadas
'''

def detect_faces(f_cascade, colored_img, scaleFactor =1.1):
	 # Se realiza una copia de la imagen
	img_copy = colored_img.copy()
	# Se convierte a formato Gray la copia de la imagen
	gray_img = convertToGray(img) 
	 # Utilizando el clasificador se procede a detectar rostros en la imagen
	faces = f_cascade.detectMultiScale(gray_img, scaleFactor=scaleFactor, minNeighbors=5)
	# Iteracion entre todas los rostros que se consiguieron en la imagen
	for(x,y,w,h) in faces: 
		 # Se dibuja un rectangulo en todos los rostros que hayan sido detectados
		cv2.rectangle(img_copy,(x,y),(x+w,y+h),(0,255,0),2)
	# Retorna la copia de la imagen original modificada
	return img_copy 

 # Imagen a la cual se detectara rostros
img = cv2.imread('new_test.png')
# Clasificador con el cual se trabajara, en nuestro caso se utilizara el haar cascade para rostros frontales
haar_face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_alt.xml') 
#Se realiza la deteccion de rostros y se guarda la copia de la imagen en la variable faces_detected_imgs
faces_detected_imgs = detect_faces(haar_face_cascade,img)
#Se muestra la imagen modificada por pantalla
cv2.imshow('Test',faces_detected_imgs)
cv2.waitKey(0)
cv2.destroyAllWindows()