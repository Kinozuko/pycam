import os

class Config(object):
	SECRET_KEY = os.environ.get('SECRECT_KEY') or 'tHiSiSJuStApRoToTyPeDoNtUsEThI420'
	MYSQL_HOST = '169.254.25.163'#'192.168.1.143'
	MYSQL_USER = 'user'
	MYSQL_PASSWORD = 'toor'
	MYSQL_DB = 'initial'