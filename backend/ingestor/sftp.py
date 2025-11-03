import logging
import paramiko
from io import BytesIO
from retry import retry


class sftp:
    def __init__(self, host, user, password) -> None:
        self.host = host
        self.username = user
        self.password = password
        self.connect()
    
    def connect(self):
        # if not self.transport.is_active():
        self.transport = paramiko.Transport((self.host,22))
        self.transport.connect(username=self.username, password=self.password)
        self.client = paramiko.SFTPClient.from_transport(self.transport)
    
    def disconnect(self):
        self.client.close()
        self.transport.close()
        self.transport.stop_thread()
    
    @retry(tries=3, jitter=[2,5], logger=None)
    def list_files(self, path: str = '.') -> list:
        filelist = []
        try:
            filelist = self.client.listdir(path)
        except OSError as e:
            if e == 'Socket is closed':
                self.connect()
                raise paramiko.sftp.SFTPError
        # except Exception as e:
        #     logging.error(f'SFTP error: {e}')
        else:
            return filelist
    
    @retry(tries=3, jitter=[2,5], logger=None)
    def get_file(self, filename: str) -> BytesIO | None:
        try:
            raw_data = BytesIO()
            self.client.getfo(remotepath=filename, fl=raw_data)
            return BytesIO(raw_data.getbuffer())
        except OSError as e:
            if e == 'Socket is closed':
                self.connect()
                raise paramiko.sftp.SFTPError
        except Exception as e:
            logging.error(f'SFTP error: {e}')
            return None
    
    @retry(tries=3, jitter=[2,5], logger=None)
    def put_file(self, file: BytesIO, filepath: str) -> bool:
        try:
            self.client.putfo(fl=file, remotepath=filepath)
            return True
        except OSError as e:
            if e == 'Socket is closed':
                self.connect()
                raise paramiko.sftp.SFTPError
        except Exception as e:
            logging.error(f'SFTP error: {e}')
            return False
    
    @retry(tries=3, jitter=[2,5], logger=None)
    def delete_file(self, file: str) -> bool:
        try:
            self.client.remove(path=file)
            return True
        except OSError as e:
            if e == 'Socket is closed':
                self.connect()
                raise paramiko.sftp.SFTPError
        except Exception as e:
            logging.error(f'SFTP error: {e}')
            return False

