try:
    import IPython
    from IPython.core.magic import Magics, magics_class, line_magic,needs_local_scope
    from IPython.core.completer import IPCompleter
except ModuleNotFoundError:
    # not interactive IPython shell
    pass

from mcshell.rconclient import LazyRconClient

SERVER_DATA = {
    'host': 'azeus.local',
    'port': '25575',
    'password': 'BnmHhjN',
}


@magics_class
class MCShell(Magics):
    def __init__(self,shell):
        super(MCShell,self).__init__(shell)
        self.ip = IPython.get_ipython()
        self.rcon_client = LazyRconClient(**SERVER_DATA)
        try:
            # _help_text = self.rcon_client.run(*['help'])
            # self.rcon_commands = {_x[0]: {"args": _x[1:]} for _x in
            #                       list(filter(lambda x: x != '', map(lambda x: x.split(' '), _help_text.split('/'))))}
            self.rcon_commands = self._build_rcon_commands()
            self.ip.set_hook('complete_command', self._complete_mc_rcon, re_key='%mc_rcon')
            self.ip.set_hook('complete_command', self._complete_mc_rcon, re_key='%mc_help')

        except Exception as e:
            print(e)
            print("Unable to start mcshell magics. Is the server running?")
            print(SERVER_DATA)
            return

        # self.rcon_commands = self._build_rcon_commands(_help_text)


    #     # print(_all_commands)
    #     self._quick_completer('%%mc_run',self.rcon_commands)
    #
    # def _quick_completer(self,cmd, completions):
    #     def do_complete(_self, event):
    #         return completions
    #     self.ip.set_hook('complete_command',do_complete, re_key = cmd)

    def _build_rcon_commands(self):
        _help_text = self.rcon_client.run(*['help'])
        _help_data = list(filter(lambda x: x != '', map(lambda x: x.split(' '), _help_text.split('/'))))[1:]
        _rcon_commands = {}
        for _help_datum in _help_data:
            _cmd = _help_datum[0]
            _cmd_data = self.rcon_client.run(*['help',_cmd])
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
            # _rcon_commands.update({_cmd: _cmd_data[1:]})
            _rcon_commands.update({_cmd: _sub_cmd_data})
        return _rcon_commands

    @needs_local_scope
    @line_magic
    def mc_help(self,line,local_ns):
        _cmd = ['help']
        if line:
            _cmd += [line]
        _help_text = self.rcon_client.run(*_cmd)
        for _help_line in _help_text.split('/')[1:]:
            print(f'/{_help_line}')


        local_ns.update(dict(rcon_help=_help_text))
        _help_data = self._build_rcon_commands()
        local_ns.update(dict(rcon_help_data=_help_data))

    def _complete_mc_help(self, ipyshell, event):
        ipyshell.user_ns.update(dict(rcon_event=event))
        text = event.symbol
        parts = event.line.split()
        ipyshell.user_ns.update(dict(rcon_event=event))

        if len(parts) == 1: # showing commands
            arg_matches = [c for c in self.rcon_commands.keys()]
            ipyshell.user_ns.update({'rcon_matches':arg_matches})
            return arg_matches
        elif len(parts) == 2 and text != '':  # completing commands
            arg_matches = [c for c in self.rcon_commands.keys() if c.startswith(text)]
            ipyshell.user_ns.update({'rcon_matches':arg_matches})
            return arg_matches

    @line_magic
    def mc_rcon(self,line):
        '''
        %mc_rcon RCON_COMMAND
        '''

        _arg_list = line.split(' ')
        print(f'Send: {line}')
        response = self.rcon_client.run(*_arg_list)
        print('Response:')
        print('-' * 100)
        if _arg_list[0] != 'help':
            print(response)
        else:
            _responses = response.split('/')
            for _response in _responses:
                print('\t' + _response)

        print('-' * 100)

    # def _complete_mc_rcon(self,ipyshell,event):
    #     ipyshell.user_ns.update(dict(rcon_event=event))
    #     text = event.symbol
    #     if not text: # Handle empty input
    #         # return [(c, c) for c in self.rcon_commands]
    #         return self.rcon_commands
    #
    #     matches = [c for c in self.rcon_commands if c.startswith(text)]
    #     return matches
    #     # return [(m, m) for m in matches]  # Return list of tuples (text, display_text)

    def _complete_mc_rcon(self, ipyshell, event):
        ipyshell.user_ns.update(dict(rcon_event=event))
        text = event.symbol
        parts = event.line.split()
        ipyshell.user_ns.update(dict(rcon_event=event))

        if len(parts) == 1: # showing commands
            arg_matches = [c for c in self.rcon_commands.keys()]
            ipyshell.user_ns.update({'rcon_matches':arg_matches})
            return arg_matches
        elif len(parts) == 2 and text != '':  # completing commands
            arg_matches = [c for c in self.rcon_commands.keys() if c.startswith(text)]
            ipyshell.user_ns.update({'rcon_matches':arg_matches})
            return arg_matches
        elif len(parts) == 2 and text == '':  # showing subcommands
            command = parts[1]
            sub_commands = list(self.rcon_commands[command].keys())
            # arg_matches = [arg for arg in args.keys() if arg.startswith(text)]
            arg_matches = [sub_command for sub_command in sub_commands]
            ipyshell.user_ns.update({'rcon_matches': arg_matches})
            return arg_matches
        elif len(parts) == 3 and text != '':  # completing subcommands
            command = parts[1]
            sub_commands = list(self.rcon_commands[command].keys())
            arg_matches = [sub_command for sub_command in sub_commands if sub_command.startswith(text)]
            ipyshell.user_ns.update({'rcon_matches': arg_matches})
            return arg_matches
        elif len(parts) == 3 and text == '':  # showing arguments
            command = parts[1]
            sub_command = parts[2]
            sub_command_args = self.rcon_commands[command][sub_command]
            arg_matches = [sub_command_arg for sub_command_arg in sub_command_args]
            ipyshell.user_ns.update({'rcon_matches': arg_matches})
            return arg_matches
        elif len(parts) > 3: # completing arguments
            command = parts[1]
            sub_command = parts[2]
            sub_command_args = self.rcon_commands[command][sub_command]
            current_arg_index = len(parts) - 3# Index of current argument
            if text == '': # showing next arguments
                arg_matches = [arg for arg in sub_command_args[current_arg_index+1]]
                ipyshell.user_ns.update({'rcon_matches': arg_matches})
                return arg_matches
            else:
                if '<' in parts[-1]:
                    pass
                elif '(' in parts[-1]:
                    pass
                else:
                    try:
                        arg_matches = [arg for arg in sub_command_args[current_arg_index+1] if arg.startswith(text)]
                        ipyshell.user_ns.update({'rcon_matches': arg_matches})
                        return arg_matches
                    except IndexError:
                        return []
                    else:
                        # No more defined arguments for this command
                        return []

        return []  # Fallback


    # @staticmethod
    # def custom_matcher(text):
    #     """
    #     Custom matcher function for IPCompleter.custom_completers.
    #     This allows for more flexible matching, e.g. partial matches
    #     """
    #
    #     # Example: Match even if the user types only part of the command
    #     # or an argument.
    #     return lambda comp_text: text.lower() in comp_text.lower() # Case-insensitive partial matching


    # @needs_local_scope
    # @line_magic
    # def xt_create_project(self,line,local_ns):
    #     '''
    #     %xt_create_project PROJECT_TYPE PARENT_PROJECT_DIR
    #     '''
    #     _line_split = line.split()
    #     if len(_line_split) != 2: raise Exception("Wrong number of arguments")
    #
    #     _project_type, _parent_project_dir = _line_split
    #
    #     _pc = ProjectFactory(_project_type,_parent_project_dir,XtooView())
    #     _pc.register_utility(Ui, XtooView())
    #
    #     _task_id = _pc.Ui().start()
    #
    #     _pc.transform()
    #     _pc.set_config_attrs()
    #     _pc.PROJECT_DIR.mkdir(exist_ok=True)
    #     _pc.save()
    #     _var_name = _pc.get('config/project-name').replace('-','_')
    #
    #     local_ns.update({_var_name:_pc})
    #
    # @needs_local_scope
    # @line_magic
    # def xt_load_project(self,line,local_ns):
    #     '''
    #     %xt_load_project PROJECT_DIR
    #     '''
    #     _line_split = line.split()
    #     if len(_line_split) != 1: raise Exception('Wrong number of arguments')
    #     _project_dir, = _line_split
    #     _pl = ProjectLoader(_project_dir,XtooView())
    #     try:
    #         _var_name = _pl.get('config/project-name').replace('-','_')
    #     except KeyError:
    #         _project_name = pathlib.Path(_pl.get('config/work-dir')).name.replace('-','_')
    #         _var_name = f'init_{_project_name}'
    #
    #     local_ns.update({_var_name:_pl})

def load_ipython_extension(ipython):
    ipython.register_magics(MCShell)
