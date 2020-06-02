import numpy as np
import cv2

# Cargar una imagen en escala de grises
# Si el segundo argumento es 1 la imagen estara en escala de colores

img = cv2.imread('test.jpg',0) 

# Crear una ventana para la imagen

cv2.imshow('image',img)

# La funcion espera los milisegundos especificados por cual evento de teclado

cv2.waitKey(0)

# Destruye todas las ventanas que fueron creadas

cv2.destroyAllWindows()

# Si se destruye una ventana particular se realizara

# cv2.destroyWindows() donde el argumento sera el nombre de la ventana a destruir

# Guardar una imagen

cv2.imwrite('new.png',img)

