import os
import pathlib
from io import StringIO
from threading import Thread,Event

import IPython
from IPython.core.magic import Magics, magics_class, line_magic,needs_local_scope
from IPython.utils.capture import capture_output
from IPython.core.completer import IPCompleter,Completer

from rich.prompt import Prompt

from mcshell.mcrepo import JsonFileRepository
from mcshell.mcclient import MCClient
from mcshell.constants import *
from mcshell.mcplayer import MCPlayer
from mcshell.mcdebugger import start_debug_server,stop_debug_server,debug_server_thread
from mcshell.mcserver import start_app_server,stop_app_server,app_server_thread
from mcshell.mcactions import *

from mcshell.mcserver import execute_power_in_thread, RUNNING_POWERS # Import helpers

from mcshell.ppmanager import *
from mcshell.ppdownloader import * # <-- Import the new class

#pycraft.settings
SHOW_DEBUG=False
SHOW_Log=False

@magics_class
class MCShell(Magics):
    def __init__(self,shell):
        super(MCShell,self).__init__(shell)

        self.ip = IPython.get_ipython()
        # self.vanilla = True if os.environ['MC_VANILLIA'] == 1 else False

        try:
            _mc_cmd_docs = pickle.load(MC_DOC_PATH.open('rb'))
        except FileNotFoundError:
            from mcshell.mcscraper import make_docs
            _mc_cmd_docs = make_docs()

        self.mc_cmd_docs = _mc_cmd_docs
        self.rcon_commands = {}

        if not MC_CREDS_PATH.exists():
            pickle.dump(SERVER_DATA,MC_CREDS_PATH.open('wb'))

        self.server_data = pickle.load(MC_CREDS_PATH.open('rb'))

        self.ip.set_hook('complete_command', self._complete_mc_run, re_key='%mc_run')
        self.ip.set_hook('complete_command', self._complete_mc_help, re_key='%mc_help')
        # self.ip.set_hook('complete_command', self._complete_mc_use_power, re_key='%mc_use_power')

        self.debug_server_thread = debug_server_thread
        self.app_server_thread = app_server_thread

        self.mc_login()

        self.active_paper_server: Optional[PaperServerManager ,None ] = None


    @line_magic
    def pp_create_world(self, line):
        """
        Creates a new, self-contained Paper server instance in its own directory.
        Usage: %pp_create_world <world_name> --version=<mc_version>
        Example: %pp_create_world my_creative_world --version=1.20.4
        """
        args = line.split()
        if not args:
            print("Usage: %pp_create_world <world_name> [--version=<mc_version>]")
            return

        world_name = args[0]
        mc_version = "1.21.4" # Default version

        # Simple argument parsing for --version flag
        for arg in args[1:]:
            if arg.startswith("--version="):
                mc_version = arg.split('=', 1)[1]

        # Define paths
        # worlds_base_dir = pathlib.Path.home() / "mc-worlds"
        # world_dir = worlds_base_dir / world_name
        # server_jars_dir = worlds_base_dir / "server_jars"
        # worlds_base_dir = MC_WORLDS_BASE_DIR
        MC_WORLDS_BASE_DIR = pathlib.Path('~').expanduser().joinpath('mc-worlds')
        world_dir = MC_WORLDS_BASE_DIR.joinpath(world_name)
        server_jars_dir = MC_WORLDS_BASE_DIR.joinpath('server-jars')

        if world_dir.exists():
            print(f"Error: A world named '{world_name}' already exists at '{world_dir}'")
            return

        print(f"Creating new world '{world_name}' for Minecraft {mc_version}...")

        # 1. Download the Paper server JAR if needed
        downloader = PaperDownloader(server_jars_dir)
        jar_path = downloader.get_jar_path(mc_version)
        if not jar_path:
            return # Stop if download failed

        # 2. Create the world directory structure
        world_dir.mkdir(parents=True)
        plugins_dir = (world_dir / "plugins")
        plugins_dir.mkdir(exist_ok=True)

        # 3. Create the eula.txt file and automatically agree to it
        try:
            with open(world_dir / "eula.txt", "w") as f:
                f.write("# By agreeing to the EULA you are indicating your agreement to our EULA (https://aka.ms/MinecraftEULA).\n")
                f.write("eula=true\n")
            print("Automatically agreed to Minecraft EULA.")
        except IOError as e:
            print(f"Error: Could not write eula.txt file. {e}")
            return

        # 4. Create the world_manifest.json file
        manifest = {
            "world_name": world_name,
            "paper_version": mc_version,
            "java_path": "java", # Assumes java is in the system's PATH
            "server_jar_path": str(jar_path.relative_to(world_dir.parent)), # Store a path relative to the world_dir
            "world_data_path": str((world_dir / "world").relative_to(world_dir)),
            "plugins": [
                "https://github.com/jdeast/FruitJuice/blob/master/target/FruitJuice-0.2.0.jar"
            ],
            "server_properties": {
                "gamemode": "creative",
                "motd": f"MC-ED World: {world_name}",
                "enable-rcon": "true",
                "rcon.port": self.server_data.get('rcon_port', 25575),
                "rcon.password": self.server_data.get('rcon_password', 'minecraft')
            }
        }

        try:
            with open(world_dir / "world_manifest.json", "w") as f:
                json.dump(manifest, f, indent=4)
            print(f"Created world manifest at: {world_dir / 'world_manifest.json'}")
        except IOError as e:
            print(f"Error: Could not write world_manifest.json file. {e}")
            return

        # 4. Install the plugins listed in the manifest
        plugin_urls = manifest.get("plugins", [])
        if plugin_urls:
            downloader.install_plugins(plugin_urls, plugins_dir)

        print(f"\nWorld '{world_name}' created successfully.")
        print(f"To start it, run: %pp_start_world {world_name}")
    @line_magic
    def pp_start_world(self, line):
        """
        Starts a Paper server for a given world name.
        If another server is running, it will be stopped first.
        Usage: %pp_start_world <world_name>
        """
        world_name = line.strip()
        if not world_name:
            print("Error: Please provide a world name. Usage: %pp_start <world_name>")
            return

        # Stop any currently active server session first
        if self.active_paper_server and self.active_paper_server.is_alive():
            print(f"Stopping the currently active server for world '{self.active_paper_server.world_name}'...")
            # First, stop the mc-ed app server that's connected to it
            stop_app_server() # Your existing function
            # Then, stop the Paper server itself
            self.active_paper_server.stop()

        # Define the directory for the new world
        world_directory = pathlib.Path.home() / "mc-worlds" / world_name

        # For now, we assume the directory exists.
        # The %pp_create magic would be responsible for actually creating it.
        if not world_directory.exists():
            print(f"Error: World directory does not exist at '{world_directory}'.")
            print(f"Please create it first with: %pp_create_world {world_name}")
            return

        print(f"--- Starting new session for world: {world_name} ---")

        # 1. Start the Paper server
        self.active_paper_server = PaperServerManager(world_name, world_directory)
        self.active_paper_server.start()

        if not self.active_paper_server.is_alive():
            print("Could not start Paper server. Aborting.")
            return

        # 2. Start the mc-ed application server
        # This assumes your %mc_start_app logic is moved into a helper
        # that we can call here.
        # For now, we'll just print a message.
        print("Paper server is running. You should now start the app server.")
        print("Example: %mc_start_app")

    def _send(self,kind,*args):
        assert kind in ('help','run','data')

        _rcon_client = self.get_client()
        try:
            if kind == 'run':
                _response = _rcon_client.run(*args)
            elif kind == 'data':
                _response = _rcon_client.data(*args)
            elif kind == 'help':
                _response = _rcon_client.help(*args)
            #print(f"[green]MCSHell running and connected to {SERVER_DATA['host']}[/]")
            return _response
        except ConnectionRefusedError as e:
            print("[red bold]Unable to send command. Is the server running?[/]")
            pprint(self.server_data)
            raise e
        except (WrongPassword, IncorrectPasswordError) as e:
            print("[red bold]The password is wrong. Use %mc_login reset[/]")
            raise e

    def get_client(self):
        if self.server_data is None:
            self.mc_login()
        return MCClient(**self.server_data)

    def get_player(self,name):
        if self.server_data is None:
            self.mc_login()
        return MCPlayer(name, **self.server_data)

    def help(self,*args):
        return self._send('help', *args)
    def run(self,*args):
        return self._send('run',*args)
    def data(self,*args,**server_data):
        return self._send('data',*args)

    @property
    def commands(self):
        _rcon_commands = {}
        if not self.rcon_commands:
            try:
                # TODO: see self.mc_help
                # _help_text = self.run('minecraft:help')
                # _help_text = self.run('help')
                _help_text = self.help()
            except:
                return _rcon_commands

            _help_data = list(filter(lambda x: x != '', map(lambda x: x.split(' '), _help_text.split('/'))))[1:]
            for _help_datum in _help_data:
                _cmd = _help_datum[0]
                if 'minecraft:' in _cmd:
                    _cmd = _cmd.split(':')[1]
                try:
                    # _cmd_data = self.run(*['help',_cmd])
                    _cmd_data = self.help(_cmd)
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
    def mc_login(self,line=''):
        '''
        %mc_login
        '''

        server_data = {}

        server_data['host'] = Prompt.ask('Server Address:',default=self.server_data['host'])
        server_data['port'] = int(Prompt.ask('Server Port:',default=str(self.server_data['port'])))
        server_data['server_type'] = Prompt.ask('Server Type:',default=self.server_data['server_type'])
        server_data['password'] = Prompt.ask('Server Password:',password=True)

        pickle.dump(server_data,MC_CREDS_PATH.open('wb'))

        self.server_data = server_data

        try:
            self.get_client().help()
        except Exception as e:
            print("[red bold]login failed[/]")

    @line_magic
    def mc_server_info(self,line):
        _mcc = self.get_client()
        pprint(self.server_data)

    @line_magic
    def mc_help(self,line):
        '''
        %mc_help [COMMAND]
        '''

        # TODO:
        # for paper
        # _cmd = ['minecraft:help']
        # for vanilla
        # _cmd = ['help']
        _cmd = []
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
            # try:
                # _help_text = self.run(*_cmd)
            _help_text = self.help(*_cmd)
            # except:
            #     print('hwat happend?')
            #     return
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

    def _complete_mc_run(self, ipyshell, event):
        ipyshell.user_ns.update(
            dict(
                rcon_event=event,
                rcon_symbol=event.symbol,
                rcon_line=event.line,
                rcon_cursor_pos=event.text_until_cursor)
        ) # Capture ALL event data IMMEDIATELY

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

    @needs_local_scope
    @line_magic
    def mc_client(self,line,local_ns):
        _uuid = str(uuid.uuid1())[:4]
        _var_name = f"mcc_{_uuid}"
        print(f"requested client will be available as {_var_name} locally")
        local_ns[_var_name] = self.get_client()

    @needs_local_scope
    @line_magic
    def mc_player(self, line, local_ns):

        _line_parts = line.strip().split()
        assert len(_line_parts) == 1
        _player_name = _line_parts.pop()
        print(f"requested player will be available as the variable {_player_name} locally")
        local_ns[_player_name] = MCPlayer(_player_name,**self.server_data).build()

    # @needs_local_scope
    # @line_magic
    # def mc_create_script(self,line,local_ns):
    #     _uuid = str(uuid.uuid1())[:4]
    #     _var_name = f"power_{_uuid}"
    #     _script_dir = pathlib.Path('.').absolute().joinpath('powers')
    #     print(_script_dir)
    #     if not _script_dir.exists():
    #         print(f"Creating a directory {_script_dir} to hold powers for debugging")
    #         _script_dir.mkdir(exist_ok=True)
    #     _script_path = pathlib.Path('./powers').joinpath(f'{_var_name}.py')
    #     print(f"Saving your new power as {_script_path}")
    #     _script_path.write_text(line)
    #     # local_ns.update({_var_name: line})

    @line_magic
    def mc_create_script(self, line):
        """
        Receives a block of Python code from the mc-ed editor,
        saves it to a uniquely named file in powers/blockcode.
        """
        code_to_save = line
        if not code_to_save:
            print("Received empty code block. No script created.")
            return

        try:
            # Create a unique filename for the power
            power_dir = pathlib.Path("./powers/blockcode")
            power_dir.mkdir(parents=True, exist_ok=True)

            # Generate a unique suffix for the filename
            file_hash = uuid.uuid4().hex[:6]
            filename = f"power_{file_hash}.py"
            filepath = power_dir / filename

            with open(filepath, 'w') as f:
                f.write(code_to_save)

            print(f"Successfully saved power to: {filepath}")
            print(f"To use it, you can now run:\nfrom powers.blockcode.{filename.replace('.py','')} import *")

        except Exception as e:
            print(f"Error saving script: {e}")

# ... inside your MCShell class ...

    @line_magic
    def mc_debug_and_define(self, line):
        """
        Receives code and metadata from the editor, and starts it in a
        background thread for debugging.
        """
        try:
            payload = json.loads(line)
            code_to_execute = payload.get("code")
            metadata = payload.get("metadata", {})

            try:
                # Create a unique filename for the power
                power_dir = pathlib.Path("./powers/blockcode")
                power_dir.mkdir(parents=True, exist_ok=True)

                # Generate a unique suffix for the filename
                file_hash = uuid.uuid4().hex[:6]
                filename = f"power_{file_hash}.py"
                filepath = power_dir / filename

                with open(filepath, 'w') as f:
                    f.write(code_to_execute)

                print(f"Successfully saved power to: {filepath}")
                print(f"To use it, you can now run:\nfrom powers.blockcode.{filename.replace('.py','')} import *")

            except Exception as e:
                print(f"Error saving script: {e}")

            # ... (check if payload is valid) ...

            player_name = self._get_mc_name()
            server_data = self.server_data

            # --- Start the power in a background thread ---
            execution_id = f"debug_{uuid.uuid4().hex[:6]}" # Special ID for debug runs
            cancel_event = Event()

            thread = Thread(target=execute_power_in_thread, args=(
                f"user-power-{execution_id}",execution_id, code_to_execute, player_name, server_data, {}, cancel_event
            ))
            thread.daemon = True
            thread.start()

            RUNNING_POWERS[execution_id] = {'thread': thread, 'cancel_event': cancel_event}

            # --- Save Metadata (This part remains synchronous) ---
            # power_repo = app.config.get('POWER_REPO')
            power_repo = JsonFileRepository(player_name)

            if power_repo:
                # You would likely call power_repo.save_power(metadata) here
                print(f"--- Power '{metadata.get('function_name')}' metadata defined/updated. ---")
                print(f"--- Started debug execution with ID: {execution_id} ---")
                print("--- To stop it, run: %mc_cancel_power " + execution_id + " ---")

        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    @line_magic
    def mc_cancel_power(self, line):
        """Cancels a running power by its execution ID."""
        execution_id = line.strip()
        if not execution_id:
            print("Usage: %mc_cancel_power <execution_id>")
            print("Currently running powers:", list(RUNNING_POWERS.keys()))
            return

        power_to_cancel = RUNNING_POWERS.get(execution_id)
        if power_to_cancel:
            print(f"Sending cancellation signal to power: {execution_id}")
            power_to_cancel['cancel_event'].set()
        else:
            print(f"Error: No running power found with ID: {execution_id}")

        @line_magic
        def mc_start_debug(self, line):
            """Starts the debug mcserver in a separate thread."""
            start_debug_server()

        @line_magic
        def mc_stop_debug(self, line):
            """Stops the debug mcserver thread."""
            stop_debug_server()

    def _get_mc_name(self):
        # Define the central, system-wide configuration file path
        CENTRAL_CONFIG_FILE = pathlib.Path("/etc/mc-shell/user_map.json")

        try:
            linux_user = os.getlogin()
        except OSError:
            linux_user = os.environ.get('USER')

        if not linux_user:
            return "Fatal Error: Could not determine Linux username."

        if not CENTRAL_CONFIG_FILE.exists():
            return f"Fatal Error: Server configuration file not found at {CENTRAL_CONFIG_FILE}. Please contact your administrator."

        try:
            with open(CENTRAL_CONFIG_FILE, 'r') as f:
                user_map = json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            raise f"Fatal Error: Could not read or parse server configuration file: {e}"

        # Get the authorized Minecraft name for the current Linux user
        minecraft_name = user_map.get(linux_user)

        if not minecraft_name:
            raise f"Error: Your Linux user '{linux_user}' is not registered to a Minecraft player. Please contact your administrator."

        return minecraft_name

    # @line_magic
    # def mc_start_app(self, line):
    #     """Starts the app mcserver in a separate thread."""
    #     start_app_server(self.server_data)
    @line_magic
    def mc_start_app(self, line):
        """
        Starts the mc-ed application server, getting the authorized Minecraft user
        name from the central configuration file.
        """
        minecraft_name = self._get_mc_name()
        print(f"Starting application server for authorized Minecraft player: {minecraft_name}")
        start_app_server(self.server_data,minecraft_name,self.shell)
        return

    @line_magic
    def mc_stop_app(self, line):
        """Stops the app mcserver thread."""
        stop_app_server()

    @line_magic
    def mc_server_status(self,line):
        '''Check if servers are running'''
        if self.app_server_thread and self.app_server_thread.is_alive():
            print("The application server is running")
        else:
            print("The application server is not running")
        if self.debug_server_thread and self.debug_server_thread.is_alive():
            print("The debugging server is running")
        else:
            print("The debugging server is not running")

print("The editor application is running")


def load_ipython_extension(ip):
    ip.register_magics(MCShell)

