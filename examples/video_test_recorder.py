import numpy as np
from datetime import datetime
import cv2

# Forma de grabar videos, el 0  indica la camara a utilizar

cap = cv2.VideoCapture(0) 

# Se define el codec del video asi como crear el objeto

fourcc = cv2.VideoWriter_fourcc(*'XVID')

out = cv2.VideoWriter('filename.avi',fourcc,20.0,(640,480))

while(cap.isOpened()):
	ret, frame  = cap.read()

	if ret==True:
		out.write(frame)
		cv2.imshow('frame',frame)
		if cv2.waitKey(1) & 0xFF == ord('q'):
			cv2.imwrite("new_test.png",frame)
			break
	else:
		break

cap.release()
out.release()
cv2.destroyAllWindows()