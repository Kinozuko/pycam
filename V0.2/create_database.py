# Se importa la libreria sqlite3 para python
import sqlite3

# Se realiza la conexion a una base de datos llamada database
conn = sqlite3.connect('database.db')

# Se hace uso del cursor para poder manipular la base de datos
c = conn.cursor()

# Se genera un query inicial para la base de datos
sql = """
DROP TABLE IF EXISTS persona;
CREATE TABLE persona(
				id integer unique primary key autoincrement,
				nombre varchar(50),
				apellido varchar(50), 
				cedula varchar(50)
);
"""

# Haciendo uso del cursor se ejecuta el query para crear la base de datos
c.executescript(sql)
# Se guardan los cambios realizados en la base de datos
conn.commit()
# Se cierra la conexion con la base de datos
conn.close()