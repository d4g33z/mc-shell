from mcshell.constants import *

class LazyRconClient:
    def __init__(self,host,port,password):

        self.host = host
        self.port = int(port)
        self.password = password

        self.client = None

    def __enter__(self):
        return self

    def run(self, *args):
        if self.client is None:
            self.client = Client(self.host,self.port,passwd=self.password).__enter__()
        return self.client.run(*args)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.client is not None:
            self.client.__exit__(exc_type, exc_val, exc_tb)
