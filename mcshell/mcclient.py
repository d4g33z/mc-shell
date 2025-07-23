from pyncraft.minecraft import Minecraft
from mcshell.constants import *

from functools import lru_cache
class _DEBUG:
    data = False

class MCClientException(Exception):
    pass

class MCClient:
    def __init__(self, host=MC_SERVER_HOST, port=MC_SERVER_PORT, password='', fj_port=FJ_PLUGIN_PORT):

        self.host = host
        self.port = port
        self.password = password
        self.fruit_juice_port  = fj_port



    def run(self, *args):
        """
        Note: the rcon connection is stateless; it cannot be persisted and must be
        created anew with each request
        """
        if not self.password:
            print('A password is required!')
            return

        if not args:
            raise MCClientException("Arguments required!")

        with Client(self.host,self.port,passwd=self.password) as client:
            _response = client.run(*args)

        return _response

    @lru_cache(maxsize=1)
    def py_client(self,player_name=None):
        # if self.server_type != 'paper':
        #     print('pyncraft client is only available on paper type servers')
        #     return None
        player_name = '' if player_name is None else player_name
        return Minecraft.create(address=self.host,port=self.fruit_juice_port,playerName=player_name)

    def help(self,*args):
        if not self.password:
            print('A password is required!')
            return

        # if self.server_type == 'paper':
        _help_cmd = 'minecraft:help'
        # elif self.server_type == 'vanilla':
        #     _help_cmd = 'help'
        # else:
        #     raise MCClientException("unknown server_type")
        _response = self.run(_help_cmd,*args)
        return _response

    def data(self, operation, *args):
        if not self.password:
            print('A password is required!')
            return

        _response = self.run('data', operation, *args)
        try:
            _response = _response[_response.index(':') + 1:]
            return json.loads(self._fix_json(_response.strip()))
        except Exception as e:
            if _DEBUG.data:
                print(e)
                print(_response)
            return {}

    async def data_async(self,varname,namespace,operation,*args):
        if not self.password:
            print('A password is required!')
            return
        async with AioClient(host=self.host,port=self.port,password=self.password) as client:
            _response = await client.send_cmd(' '.join(['data',operation,*args]))
        if isinstance(_response,tuple):
            _response = _response[0]
            try:
                _response = _response[_response.index(':')+1:]
                namespace.update({varname:json.loads(self._fix_json(_response))})
            except Exception as e:
                if _DEBUG.data:
                    print(e)
                    print(_response)
        else:
            namespace.update({varname:_response})


    def _fix_nbt_values(self, _text):
        """Removes NBT suffixes and converts to appropriate Python types."""
        _text = re.sub(r"(\d+)b", r"False", _text)  # Bytes to booleans
        _text = re.sub(r"(\d+)s", r"\1", _text)  # Shorts to ints
        _text = re.sub(r"(\d+)l", r"\1", _text)  # Longs to ints
        _text = re.sub(r"(\d+(?:\.\d+)?)f", r"\1", _text)  # Floats to floats
        _text = re.sub(r"(\d+(?:\.\d+)?)d", r"\1", _text)  # Doubles to floats

        # Fix NBT arrays (e.g., [I; 1, 2, 3] to [1, 2, 3])
        _text = re.sub(r"\[[BISL];\s*([^\]]+)\]", r"[\1]", _text)
        return _text

    def _fix_json(self,json_string):
        _pattern = r"(?<!\")\b(\w+):\s*"
        _fixed_string = re.sub(_pattern, r'"\1":', json_string)
        _fixed_string = self._fix_nbt_values(_fixed_string)
        _fixed_string = re.sub(rf"\s*:({RE_NON_JSON_VALUE})", r':"\1"',_fixed_string)
        _fixed_string = _fixed_string.replace('False','false').replace('True','true').replace("\'","")
        _fixed_string = _fixed_string.replace('-false','false').replace('-true','true').replace("\'","")
        return _fixed_string
