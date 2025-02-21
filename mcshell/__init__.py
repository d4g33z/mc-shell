try:
    import IPython
    from IPython.core.magic import Magics, magics_class, line_magic,needs_local_scope
    from IPython.core.completer import IPCompleter,Completer
except ModuleNotFoundError:
    # not interactive IPython shell
    pass

from mcshell.mcclient import MCClient
from mcshell.constants import *

@magics_class
class MCShell(Magics):
    def __init__(self,shell):
        super(MCShell,self).__init__(shell)

        self.ip = IPython.get_ipython()

        self.rcon_client = MCClient(**SERVER_DATA)

        try:
            _mc_cmd_docs = pickle.load(MC_DOC_PATH.open('rb'))
        except FileNotFoundError:
            from mcshell.mcscraper import make_docs
            _mc_cmd_docs = make_docs()

        self.mc_cmd_docs = _mc_cmd_docs
        self.rcon_commands = {}

        self.ip.set_hook('complete_command', self._complete_mc_run, re_key='%mc_run')
        self.ip.set_hook('complete_command', self._complete_mc_run, re_key='%mc_help')

    def run(self,*args):
        try:
            _response = self.rcon_client.run(*args)
            #print(f"[green]MCSHell running and connected to {SERVER_DATA['host']}[/]")
            return _response
        except ConnectionRefusedError as e:
            print("[red bold]Unable to send command. Is the server running?[/]")
            pprint(SERVER_DATA)
            raise e

    def data(self, *args):
        try:
            _response = self.rcon_client.data(*args)
            # print(f"[green]MCSHell running and connected to {SERVER_DATA['host']}[/]")
            return _response
        except ConnectionRefusedError as e:
            print("[red bold]Unable to start mcshell magics. Is the server running?[/]")
            pprint(SERVER_DATA)
            raise e

    # def _build_rcon_commands(self):
    @property
    def commands(self):
        if not self.rcon_commands:
            try:
                _help_text = self.run('help')
            except ConnectionRefusedError:
                return

            _help_data = list(filter(lambda x: x != '', map(lambda x: x.split(' '), _help_text.split('/'))))[1:]
            _rcon_commands = {}
            for _help_datum in _help_data:
                _cmd = _help_datum[0]
                try:
                    _cmd_data = self.run(*['help',_cmd])
                except ConnectionRefusedError:
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
                    # _rcon_commands.update({_cmd: _sub_cmd_data})
                    _rcon_commands.update({_cmd.replace('-','_'): _sub_cmd_data})
            self.rcon_commands = _rcon_commands
        return self.rcon_commands

    @line_magic
    def mc_help(self,line):
        _cmd = ['help']

        _doc_line = ''
        _doc_url = ''
        _doc_code_lines = ''
        if line:
            _line_parts = line.split()
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
            except ConnectionRefusedError:
                return
            for _help_line in _help_text.split('/')[1:]:
                _help_parts = _help_line.split()
                _help_parts[0] = _help_parts[0].replace('-','_')
                print(f'{" ".join(_help_parts)}')

    # local_ns.update(dict(rcon_help=_help_text))
        # _help_data = self._build_rcon_commands()
        # local_ns.update(dict(rcon_help_data=_help_data))

    def _complete_mc_help(self, ipyshell, event):
        ipyshell.user_ns.update(dict(rcon_event=event))
        text = event.symbol
        parts = event.line.split()
        ipyshell.user_ns.update(dict(rcon_event=event))

        if len(parts) == 1: # showing commands
            arg_matches = [c for c in self.commands.keys()]
            ipyshell.user_ns.update({'rcon_matches':arg_matches})
            return arg_matches
        elif len(parts) == 2 and text != '':  # completing commands
            arg_matches = [c for c in self.commands.keys() if c.startswith(text)]
            ipyshell.user_ns.update({'rcon_matches':arg_matches})
            return arg_matches

    @line_magic
    def mc_run(self,line):
        '''
        %mc_run RCON_COMMAND
        '''

        _arg_list = line.split(' ')
        _arg_list[0] = _arg_list[0].replace('_','-')
        print(f"Send: {' '.join(_arg_list)}")
        try:
            response = self.run(*_arg_list)
        except ConnectionRefusedError:
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
            # print(f"{response[:response.index('command') + 7]}:")


        else:
            print(response)

        print('-' * 100)


    @needs_local_scope
    @line_magic
    def mc_data(self, line,local_ns):
        '''
        '''

        _arg_list = line.split(' ')
        # supported data ops
        assert _arg_list[0] in ('get','modify','merge','remove')
        print(f"Requesting data: {' '.join(_arg_list)}")
        _uuid = str(uuid.uuid1())[:4]
        _var_name = f"data_{_arg_list[0]}_{_uuid}"
        print(f"requested data will be available as {_var_name} locally")
        # async is broken due to truncated server output
        # asyncio.run(self.rcon_client.data(_var_name,local_ns,*_arg_list))
        try:
            _data = self.data(*_arg_list)
        except:
            return
        local_ns.update({_var_name:_data})


    def _complete_mc_run(self, ipyshell, event):
        ipyshell.user_ns.update(dict(rcon_event=event, rcon_symbol=event.symbol, rcon_line=event.line, rcon_cursor_pos=event.text_until_cursor)) # Capture ALL event data IMMEDIATELY

        # ipyshell.user_ns.update(dict(rcon_event=event))

        text_to_complete = event.symbol
        line = event.line

        parts = line.split()

        # if not text:
        #     text_to_complete = ''
        # elif text.endswith('-'): # Corrected condition: Check if text ENDS with '-'
        #     text_to_complete = text[:-1]
        # else:
        #     text_to_complete = text

        ipyshell.user_ns.update(dict(rcon_text_to_complete=text_to_complete)) # Capture text_to_complete
        ipyshell.user_ns.update(dict(rcon_parts=parts)) # Capture parts

        arg_matches = []
        if len(parts) == 1: # showing commands
            arg_matches = [c for c in self.commands.keys()]
        elif len(parts) == 2 and text_to_complete != '':  # completing commands
            arg_matches = [c for c in self.commands.keys() if c.startswith(text_to_complete)]
        elif len(parts) == 2 and text_to_complete == '':  # showing subcommands
            command = parts[1]
            sub_commands = list(self.commands[command].keys())
            arg_matches = [sub_command for sub_command in sub_commands]
        elif len(parts) == 3 and text_to_complete != '':  # completing subcommands
            command = parts[1]
            sub_commands = list(self.commands[command].keys())
            arg_matches = [sub_command for sub_command in sub_commands if sub_command.startswith(text_to_complete)]
        elif len(parts) == 3 and text_to_complete == '':  # showing arguments
            command = parts[1]
            sub_command = parts[2]
            sub_command_args = self.commands[command][sub_command]
            arg_matches = [sub_command_arg for sub_command_arg in sub_command_args]
        elif len(parts) > 3: # completing arguments
            command = parts[1]
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

def load_ipython_extension(ip):
    ip.register_magics(MCShell)

