from pycam.ssh import SSHConnection

host = "192.168.1.143"
username = "pi"
pw = "root"


dest = "/home/pi/PyCam/app/templates/base.html"
dest1 = "/home/pi/PyCam/app/templates/view_guest.html"
dest2 = "/home/pi/PyCam/app/routes.py"
dest3 = "/home/pi/PyCam/pycam/pycam.py"
dest4 = "/home/pi/PyCam/trainer/trainer.yml"
dest5 = "/home/pi/PyCam/pycam/ssh.py"
dest6 = "/home/pi/PyCam/app/templates/view_students.html"
dest7 = "/home/pi/PyCam/app/templates/view_padm.html"
dest8 = "/home/pi/PyCam/app/templates/view_pobrero.html"
dest9 = "/home/pi/PyCam/app/forms.py"
dest10 = "/home/pi/PyCam/app/templates/index.html"
dest11 = "/home/pi/PyCam/app/templates/view_users.html"


orig = "C:\\Users\\victo\\Desktop\\TESIS\\PyCam\\V1.0\\app\\templates\\base.html"
orig1 = "C:\\Users\\victo\\Desktop\\TESIS\\PyCam\\V1.0\\app\\templates\\view_guest.html"
orig2= "C:\\Users\\victo\\Desktop\\TESIS\\PyCam\\V1.0\\app\\routes.py"
orig3 = "C:\\Users\\victo\\Desktop\\TESIS\\PyCam\\V1.0\\pycam\\pycam.py"
orig4 = "C:\\Users\\victo\\Desktop\\TESIS\\PyCam\\V1.0\\trainer\\trainer.yml"
orig5 = "C:\\Users\\victo\\Desktop\\TESIS\\PyCam\\V1.0\\pycam\\ssh.py"
orig6 = "C:\\Users\\victo\\Desktop\\TESIS\\PyCam\\V1.0\\app\\templates\\view_students.html"
orig7 = "C:\\Users\\victo\\Desktop\\TESIS\\PyCam\\V1.0\\app\\templates\\view_padm.html"
orig8 = "C:\\Users\\victo\\Desktop\\TESIS\\PyCam\\V1.0\\app\\templates\\view_pobrero.html"
orig9 = "C:\\Users\\victo\\Desktop\\TESIS\\PyCam\\V1.0\\app\\forms.py"
orig10 = "C:\\Users\\victo\\Desktop\\TESIS\\PyCam\\V1.0\\app\\templates\\index.html"
orig11 = "C:\\Users\\victo\\Desktop\\TESIS\\PyCam\\V1.0\\app\\templates\\view_users.html"


ssh = SSHConnection(host,username,pw)
#ssh.put(orig,dest)
#ssh.put(orig1,dest1)
#ssh.put(orig2,dest2)
#ssh.put(orig3,dest3)
#ssh.put(orig4,dest4)
#ssh.put(orig5,dest5)
#ssh.put(orig6,dest6)
#ssh.put(orig7,dest7)
#ssh.put(orig8,dest8)
#ssh.put(orig9,dest9)
#ssh.put(orig10,dest10)
#ssh.put(orig11,dest11)
ssh.close()