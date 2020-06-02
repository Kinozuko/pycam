import paramiko
 
class SSHConnection(object):

    def __init__(self, host, username, password, port=22):
        # Se incializan las conexiones
        self.sftp = None
        self.sftp_open = False
        # Se abre el transporte utilizando el host y puerto dados
        self.transport = paramiko.Transport((host, port))
        # se realiza la conexion a traves del transporte
        self.transport.connect(username=username, password=password)
 
    def _openSFTPConnection(self):
        # Se abre la conexion si esta no se encuentra abierta   
        if not self.sftp_open:
            self.sftp = paramiko.SFTPClient.from_transport(self.transport)
            self.sftp_open = True
 
    def get(self, remote_path, local_path=None):
        # Se abre la conexion SFTP para transferencia de archivos
        self._openSFTPConnection()        
        # Se transfiere el archivo de la maquina remota a la maquina local
        self.sftp.get(remote_path, local_path)        
 
    def put(self, local_path, remote_path=None):
        # Se abre la conexion SFTP para transferencia de archivos
        self._openSFTPConnection()
        # Se transfiere el archivo de la maquina local a la maquina remota
        self.sftp.put(local_path, remote_path)
    
    def create_folder(self,remote_path):
        """
        Crea un directoria en la maquina remota
        """
        self._openSFTPConnection()
        try:
            self.sftp.chdir(remote_path)
        except IOError:
            self.sftp.mkdir(remote_path)
            self.sftp.chdir(remote_path)
    
    def close(self):
        # Se cierra la conexion SFTP y SSH
        if self.sftp_open:
            self.sftp.close()
            self.sftp_open = False
        self.transport.close()