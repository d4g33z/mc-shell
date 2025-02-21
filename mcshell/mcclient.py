from mcshell.constants import *


class MCClient:
    def __init__(self,host,port,password):

        self.host = host
        self.port = int(port)
        self.password = password

    def run(self, *args):
        with  Client(self.host, self.port, passwd=self.password) as client:
            _response = client.run(*args)
        return _response

    # this is broken; long server responses are truncated
    async def data_async(self,varname,namespace,operation,*args):
        async with AioClient(host=self.host,port=self.port,password=self.password) as client:
            _response = await client.send_cmd(' '.join(['data',operation,*args]))
        # _response = await AioClient(*['data',operation,*args],host=self.host,port=self.port,passwd=self.password)
        if isinstance(_response,tuple):
            _response = _response[0]
            _response = _response[_response.index(':')+1:]
            namespace.update({varname:json.loads(self._fix_json(_response))})
        else:
            namespace.update({varname:_response})
        # return _response

    def data(self,operation,*args):
        _response = self.run('data',operation,*args)
        if _response.split()[0] == 'No':
            print(_response)
            return
        _response = _response[_response.index(':')+1:]
        return json.loads(self._fix_json(_response))

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
        return _fixed_string
