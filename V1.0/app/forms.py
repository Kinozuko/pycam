from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, FloatField
from wtforms.validators import DataRequired
from wtforms.fields.html5 import DateField

_tipo_usuario = {'adm' : 'Adiministrador',  'gaceta' : 'Vigilancia', 'registro' : 'Registro'}
_semestres = {0:'1ro',1:'2do',3:'3ro',4:'4to',5:'5to',6:'6to',7:'7mo',8:'8vo',9:'9no',10:'10mo'}

class LoginForm(FlaskForm):
	username = StringField('Usuario',validators=[DataRequired()])
	password = PasswordField('Clave',validators=[DataRequired()])
	submit = SubmitField('Iniciar Sesion')

class UserRegister(FlaskForm):
	usuario = StringField('Usuario', validators=[DataRequired()])
	password = PasswordField('Clave',validators=[DataRequired()])
	confirm_password = PasswordField('Confirmar Clave',validators=[DataRequired()])
	tipo = SelectField('Tipo de usuario', choices = [('adm','Adiministrador') , ('gaceta','Vigilancia'), ('registro','Registro'),],validators = [DataRequired()])
	submit = SubmitField('Registrar')

class StudentRegister(FlaskForm):
	nombre = StringField('Nombre',validators=[DataRequired()])
	apellido = StringField('Apellido',validators=[DataRequired()])
	cedula = StringField('Cedula',validators=[DataRequired()])
	carrera = SelectField('Carrera',choices=[('ie','Ing. Electronica'),('iet','Ing. en Telecomunicaciones'),])
	semestre = SelectField('Semestre', choices = [('1ro','1ro') , ('2do','2do') , ('3ro','3ro') ,('4to','4to') , ('5to','5to') , ('6to','6to') , ('7mo','7mo') , ('8vo','8vo') , ('9no','9no') , ('10mo','10mo') , ],validators = [DataRequired()])
	submit = SubmitField('Registrar')

class PersonalAdmRegister(FlaskForm):
	nombre = StringField('Nombre',validators=[DataRequired()])
	apellido = StringField('Apellido',validators=[DataRequired()])
	cedula = StringField('Cedula',validators=[DataRequired()])
	costo_hora = FloatField('Costo por Hora')
	submit = SubmitField('Registrar')

class PersonalRegister(FlaskForm):
	nombre = StringField('Nombre',validators=[DataRequired()])
	apellido = StringField('Apellido',validators=[DataRequired()])
	cedula = StringField('Cedula',validators=[DataRequired()])
	sueldo = FloatField('Sueldo')
	submit = SubmitField('Registrar')

class AddItem(FlaskForm):
	cedula = StringField('Cedula',validators=[DataRequired()])
	equipo = StringField('Objetos a Registrar',validators=[DataRequired()])
	submit = SubmitField('Registrar Equipo(s)')

class Guest(FlaskForm):
	nombre = StringField('Nombre',validators=[DataRequired()])
	apellido = StringField('Apellido',validators=[DataRequired()])
	cedula = StringField('Cedula',validators=[DataRequired()])
	motivo = StringField('Motivo')
	equipo = StringField('Objetos a Registrar')
	cedula_persona = StringField('Cedula del Estudiante que Otorga Acceso')
	submit = SubmitField('Registrar')

class DateForm(FlaskForm):
	fecha = DateField('Seleccione Fecha de Busqueda',format='%Y-%m-%d')
	submit = SubmitField('Buscar')

class GuestCheck(FlaskForm):
	cedula = StringField('Cedula',validators=[DataRequired()])
	submit = SubmitField('Registrar Salida')