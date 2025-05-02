import IPython
from IPython.core.magic import Magics, magics_class, line_magic,needs_local_scope
from IPython.utils.capture import capture_output
from IPython.core.completer import IPCompleter,Completer

from rich.prompt import Prompt

from mcshell.client import MCClient
from mcshell.constants import *
from mcshell.mcserver import start_flask_server,stop_flask_server

@magics_class
class MCShell(Magics):
    def __init__(self,shell):
        super(MCShell,self).__init__(shell)

        self.ip = IPython.get_ipython()
        self.vanilla = True if os.environ['MC_VANILLIA'] == 1 else False

        try:
            _mc_cmd_docs = pickle.load(MC_DOC_PATH.open('rb'))
        except FileNotFoundError:
            from mcshell.mcscraper import make_docs
            _mc_cmd_docs = make_docs()

        self.mc_cmd_docs = _mc_cmd_docs
        self.rcon_commands = {}

        if MC_CREDS_PATH.exists():
            self.SERVER_DATA = pickle.load(MC_CREDS_PATH.open('rb'))
        else:
            self.SERVER_DATA = None

        self.ip.set_hook('complete_command', self._complete_mc_run, re_key='%mc_run')
        self.ip.set_hook('complete_command', self._complete_mc_help, re_key='%mc_help')
        self.ip.set_hook('complete_command', self._complete_mc_use_power, re_key='%mc_use_power')


    def _send(self,kind,*args):
        assert kind in ('run','data')

        if self.SERVER_DATA is None:
            self.mc_login('reset')
        _rcon_client = MCClient(**self.SERVER_DATA,vanilla=self.vanilla)
        try:
            if kind == 'run':
                _response = _rcon_client.run(*args)
            elif kind == 'data':
                _response = _rcon_client.data(*args)
            #print(f"[green]MCSHell running and connected to {SERVER_DATA['host']}[/]")
            return _response
        except ConnectionRefusedError as e:
            print("[red bold]Unable to send command. Is the server running?[/]")
            pprint(self.SERVER_DATA)
            raise e
        except (WrongPassword, IncorrectPasswordError) as e:
            print("[red bold]The password is wrong. Use %mc_login reset[/]")
            raise e

    def run(self,*args):
        return self._send('run',*args)
    def data(self,*args):
        return self._send('data',*args)

    @property
    def commands(self):
        _rcon_commands = {}
        if not self.rcon_commands:
            try:
                _help_text = self.run('minecraft:help')
            except:
                return _rcon_commands

            _help_data = list(filter(lambda x: x != '', map(lambda x: x.split(' '), _help_text.split('/'))))[1:]
            for _help_datum in _help_data:
                _cmd = _help_datum[0]
                if 'minecraft:' in _cmd:
                    _cmd = _cmd.split(':')[1]
                try:
                    _cmd_data = self.run(*['help',_cmd])
                except:
                    return
                if not _cmd_data:
                    # found a shortcut command like xp -> experience
                    continue
                _cmd_data = list(map(lambda x:x.split()[1:],_cmd_data.split('/')))
                _sub_cmd_data = {}
                for _sub_cmd_datum in _cmd_data[1:]:
                    if not _sub_cmd_datum[0][0]  in ('<','[','('):
                        _sub_cmd_data.update({_sub_cmd_datum[0]: _sub_cmd_datum[1:]})
                    else:
                        # TODO what about commands without sub-commands?
                        _sub_cmd_data.update({' ': _sub_cmd_datum})
                    _rcon_commands.update({_cmd.replace('-','_'): _sub_cmd_data})
            self.rcon_commands = _rcon_commands
        return self.rcon_commands

    @line_magic
    def mc_login(self,line):
        '''
        %mc_login [reset]
        '''
        if not self.SERVER_DATA or  line.strip() == 'reset':
            self.SERVER_DATA = {}
            self.SERVER_DATA['host'] = Prompt.ask('Server Address:',default='localhost')
            self.SERVER_DATA['port'] = Prompt.ask('Server Port:',default='25575')
            self.SERVER_DATA['password'] = Prompt.ask('Server Password:',password=True)
            pickle.dump(self.SERVER_DATA,MC_CREDS_PATH.open('wb'))

    @line_magic
    def mc_help(self,line):
        '''
        %mc_help [COMMAND]
        '''

        _cmd = ['minecraft:help']

        _doc_line = ''
        _doc_url = ''
        _doc_code_lines = ''
        if line:
            _line_parts = line.split()
            if 'minecraft:' in _line_parts[0]:
                _line_parts[0] = _line_parts[0].split(':')[1]
            _doc_line,_doc_url,_doc_code_lines = self.mc_cmd_docs.get(_line_parts[0],('','',''))
            _line_parts[0] = _line_parts[0].replace('_', '-')
            _cmd += [' '.join(_line_parts)]

        if _doc_line and _doc_url:
            print(_doc_line)
            print(_doc_url)

        print()
        if _doc_code_lines:
            for _doc_code_line in _doc_code_lines:
                print(_doc_code_line)
        else:
            try:
                _help_text = self.run(*_cmd)
            except:
                return
            for _help_line in _help_text.split('/')[1:]:
                _help_parts = _help_line.split()
                _help_parts[0] = _help_parts[0].replace('-','_')
                print(f'{" ".join(_help_parts)}')

    def _complete_mc_help(self, ipyshell, event):
        ipyshell.user_ns.update(dict(rcon_event=event))
        text = event.symbol
        parts = event.line.split()
        ipyshell.user_ns.update(dict(rcon_event=event))

        arg_matches= []
        if len(parts) == 1: # showing commands
            arg_matches = [c for c in self.commands.keys()]
            ipyshell.user_ns.update({'rcon_matches':arg_matches})
        elif len(parts) == 2 and text != '':  # completing commands
            arg_matches = [c for c in self.commands.keys() if c.startswith(text)]
            ipyshell.user_ns.update({'rcon_matches':arg_matches})

        return arg_matches

    @line_magic
    def mc_run(self,line):
        '''
        %mc_run COMMAND
        '''

        _arg_list = line.split(' ')
        _arg_list[0] = _arg_list[0].replace('_','-')
        print(f"Send: {' '.join(_arg_list)}")
        try:
            response = self.run(*_arg_list)
            if response == '':
                return
        except:
            return
        if not response:
            return
        
        print('Response:')
        print('-' * 100)
        if _arg_list[0] == 'help':
            _responses = response.split('/')
            for _response in _responses:
                print('\t' + _response)
        elif response.split()[0] == 'Unknown':
            print("[red]Error in usage:[/]")
            self.mc_help(line)
        else:
            print(response)
        print('-' * 100)


    @needs_local_scope
    @line_magic
    def mc_data(self, line,local_ns):
        '''
        %mc_data OPERATION ARGUMENTS
        '''

        _arg_list = line.split(' ')
        # supported data ops
        try:
            assert _arg_list[0] in ('get','modify','merge','remove')
        except AssertionError:
            print(f"Wrong arguments!")
            return
        print(f"Requesting data: {' '.join(_arg_list)}")
        _uuid = str(uuid.uuid1())[:4]
        _var_name = f"data_{_arg_list[0]}_{_uuid}"
        print(f"requested data will be available as {_var_name} locally")
        # async is broken due to truncated server output
        # asyncio.run(self.rcon_client.data(_var_name,local_ns,*_arg_list))
        #try:
        _data = self.data(*_arg_list)
        #except:
        #    return
        local_ns.update({_var_name:_data})


    def _complete_mc_run(self, ipyshell, event):
        ipyshell.user_ns.update(dict(rcon_event=event, rcon_symbol=event.symbol, rcon_line=event.line, rcon_cursor_pos=event.text_until_cursor)) # Capture ALL event data IMMEDIATELY

        text_to_complete = event.symbol
        line = event.line

        parts = line.split()

        ipyshell.user_ns.update(dict(rcon_text_to_complete=text_to_complete)) # Capture text_to_complete
        ipyshell.user_ns.update(dict(rcon_parts=parts)) # Capture parts
        if len(parts) >= 2:
            command = parts[1]
            if 'minecraft:' in command:
                command = command.split(':')[1]
        arg_matches = []
        if len(parts) == 1: # showing commands
            arg_matches = [c for c in self.commands.keys()]
        elif len(parts) == 2 and text_to_complete != '':  # completing commands
            arg_matches = [c for c in self.commands.keys() if c.startswith(text_to_complete)]
        elif len(parts) == 2 and text_to_complete == '':  # showing subcommands
            # command = parts[1]
            sub_commands = list(self.commands[command].keys())
            arg_matches = [sub_command for sub_command in sub_commands]
        elif len(parts) == 3 and text_to_complete != '':  # completing subcommands
            # command = parts[1]
            sub_commands = list(self.commands[command].keys())
            arg_matches = [sub_command for sub_command in sub_commands if sub_command.startswith(text_to_complete)]
        elif len(parts) == 3 and text_to_complete == '':  # showing arguments
            # command = parts[1]
            sub_command = parts[2]
            sub_command_args = self.commands[command][sub_command]
            arg_matches = [sub_command_arg for sub_command_arg in sub_command_args]
        elif len(parts) > 3: # completing arguments
            # command = parts[1]
            sub_command = parts[2]
            sub_command_args = self.commands[command][sub_command]
            current_arg_index = len(parts) - 3# Index of current argument
            if text_to_complete == '': # showing next arguments
                arg_matches = [arg for arg in sub_command_args[current_arg_index+1]]
            else:
                try:
                    arg_matches = [arg for arg in sub_command_args[current_arg_index+1] if arg.startswith(text_to_complete)]
                except IndexError:
                    return []

        ipyshell.user_ns.update({'rcon_matches': arg_matches})
        return arg_matches # Fallback

    @needs_local_scope
    @line_magic
    def mc_create_script(self,line,local_ns):
        _uuid = str(uuid.uuid1())[:4]
        _var_name = f"power_{_uuid}"
        _script_path = pathlib.Path('powers/blockcode').joinpath(f'{_var_name}.py')
        _script_path.write_text(line)
        local_ns.update({_var_name: line})
        print(f"requested will be available as {_var_name}.py locally")

    @line_magic
    def mc_use_power(self,line):
        _power_name = line
        _script_path = pathlib.Path('powers').joinpath(f'{_power_name}.py')
        if _script_path.exists():
            self.ip.run_line_magic('run',str(_script_path))
        else:
            print('error!')

    def _complete_mc_use_power(self,ipyshell,event):
        ipyshell.user_ns.update(dict(rcon_event=event, rcon_symbol=event.symbol, rcon_line=event.line, rcon_cursor_pos=event.text_until_cursor)) # Capture ALL event data IMMEDIATELY

        _powers = pathlib.Path('powers').glob('*.py')
        text_to_complete = event.symbol
        line = event.line
        return [p.name.split('.')[0] for p in _powers if str(p.name).startswith(text_to_complete)]

    @line_magic
    def mc_start_server(self, line):
        """Starts the Flask mcserver in a separate thread."""
        start_flask_server()
        return "Flask mcserver started in a thread."

    @line_magic
    def mc_stop_server(self, line):
        """Stops the Flask mcserver thread."""
        stop_flask_server()
        return "Stopping Flask mcserver thread..."

def load_ipython_extension(ip):
    ip.register_magics(MCShell)

