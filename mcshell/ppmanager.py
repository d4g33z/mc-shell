import subprocess
import pexpect
import threading
from pathlib import Path

from mcshell.constants import *

class PaperServerManager:
    """Manages the lifecycle of a single Paper server subprocess using pexpect."""

    def __init__(self, world_name: str, world_directory: Path):
        self.world_name = world_name
        self.world_directory = world_directory
        self.process: Optional[pexpect.spawn , None] = None
        self.thread: Optional[threading.Thread , None] = None

        self.world_manifest = json.load(self.world_directory.joinpath('world_manifest.json').open('br'))
        self.jar_path = self.world_directory.parent.joinpath(self.world_manifest.get('server_jar_path'))

    def _run_initialization(self):
        """
        Runs the server once with --initSettings to generate config files, then exits.
        """
        if (self.world_directory / "server.properties").exists():
            print("Configuration files already exist. Skipping initialization run.")
            return True

        print("--- Running server initialization to generate config files... ---")
        command = ['java', '-jar', str(self.jar_path), '--initSettings']

        try:
            # We use run() here because this is a short, blocking process.
            init_process = subprocess.run(
                command,
                cwd=self.world_directory,
                capture_output=True,
                text=True,
                check=True # Raise an exception if it fails
            )
            print("--- Server initialization run complete. ---")
            return True
        except subprocess.CalledProcessError as e:
            print("! Error during server initialization run.")
            print(f"  Return Code: {e.returncode}")
            print(f"  Output:\n{e.stdout}")
            print(f"  Error Output:\n{e.stderr}")
            return False
        except FileNotFoundError:
            print("Error: 'java' command not found. Is Java installed and in your PATH?")
            return False

    def apply_manifest_settings(self):
        """
        Reads the world_manifest.json and applies its settings to the
        server.properties file and to plugins/FruitJuice/config.yml
        """
        # First, ensure config files exist by running the init command.
        if not self._run_initialization():
            return # Abort if initialization fails

        print("--- Applying settings from world_manifest.json to server.properties ---")

        try:
            settings_to_apply = self.world_manifest.get("server_properties", {})
            if not settings_to_apply:
                print("No server_properties found in manifest. Using defaults.")
                return

            # 2. Read the existing server.properties file
            properties_path = self.world_directory / "server.properties"
            properties = {}
            with open(properties_path, 'r') as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        properties[key] = value

            # 3. Update the properties with values from the manifest
            for key, value in settings_to_apply.items():
                if 'password' not in key:
                    print(f"  Setting '{key}' = '{value}'")
                properties[key] = str(value)

            # 4. Write the updated properties back to the file
            with open(properties_path, 'w') as f:
                f.write("#Minecraft server properties\n")
                f.write(f"#(last modified by mc-shell)\n")
                for key, value in properties.items():
                    f.write(f"{key}={value}\n")

            print("--- server.properties updated successfully. ---")
            #
            print("--- Applying settings from world_manifest.json to FruitJuice/config.yml ---")

            fj_config_path = self.world_directory / "plugins" / "FruitJuice" / "config.yml"
            fj_config_path.parent.mkdir(parents=True,exist_ok=True)


            fj_data = self.world_manifest['FruitJuice']

            with fj_config_path.open('w') as file:
                yaml.dump(fj_data, file, sort_keys=False)

            print("--- config.yml updated successfully. ---")

        except FileNotFoundError:
            print(f"Error: Could not find manifest or server.properties file.")
        except Exception as e:
            print(f"An error occurred while applying settings: {e}")

    def _execute_server(self):
        """
        The main execution function. Starts the Paper server and logs its
        output in real-time without blocking the parent thread.
        """
        # Command to run the server from within its specific world directory
        command = ' '.join([
            'java',
            '-Xms2G', '-Xmx2G', # Example memory settings
            '-jar', str(self.jar_path),
            'nogui'
        ])


        print(f"Starting Paper server for world '{self.world_name}'...")
        print(f"  > Directory: {self.world_directory}")

        try:
            self.process = pexpect.spawn(
                command,
                cwd=str(self.world_directory),
                encoding='utf-8'
            )

            # This non-blocking loop continuously polls for new output.
            while self.process.isalive():
                try:
                    # expect() waits for either a newline or a timeout.
                    # We give it a short timeout (e.g., 0.1s) to make the loop responsive.
                    index = self.process.expect(['\r\n', pexpect.TIMEOUT, pexpect.EOF], timeout=0.1)

                    # If index is 0, it means we matched a newline.
                    if index == 0:
                        # self.process.before contains all the text before the match.
                        line = self.process.before

                        if "Thread RCON Client" in line.strip():
                            continue # Skip this line and do not print it
                        elif "FruitJuice" in line.strip():
                            continue
                        if line:
                            sys.stdout.write(f"[{self.world_name}] {line}\n")
                            sys.stdout.flush()

                except pexpect.exceptions.TIMEOUT:
                    # This is the expected behavior when the server is idle.
                    # We simply continue the loop and check again.
                    continue
                except pexpect.exceptions.EOF:
                    # The process has closed the connection.
                    print(f"[{self.world_name}] Server stream closed (EOF).")
                    break
                except Exception as e:
                    print(f"[{self.world_name}] Error reading from server process: {e}")
                    break

        except Exception as e:
            print(f"An error occurred while launching the Paper server: {e}")
        finally:
            print(f"\nPaper server process for world '{self.world_name}' has terminated.")
            if self.process and self.process.isalive():
                self.process.close(force=True)
            self.process = None

    def start(self):
        """Starts the Paper server in a new background management thread."""
        if self.is_alive():
            print(f"Server for world '{self.world_name}' is already running.")
            return

        self.apply_manifest_settings()
        self.thread = threading.Thread(target=self._execute_server, daemon=True)
        self.thread.start()

        # Give the server time to initialize. A better method is to parse
        # the output for the "Done!" message.
        print("Waiting for server to initialize...")
        time.sleep(15)

        if not self.is_alive():
            print(f"Error: Failed to start the server for world '{self.world_name}'. Check logs for details.")

    def stop(self):
        """Stops the running Paper server by sending the 'stop' command."""
        if not self.is_alive():
            print(f"Server for '{self.world_name}' is not running.")
            return

        print(f"Sending 'stop' command to Paper server for '{self.world_name}'...")
        try:
            # sendline automatically adds the newline character.
            self.process.sendline('stop')
            # Give the thread time to process the stop command and exit gracefully
            self.thread.join(timeout=30)
        except pexpect.exceptions.ExceptionPexpect as e:
            print(f"Failed to send 'stop' command cleanly: {e}. Terminating.")
            self.process.terminate()

    def is_alive(self) -> bool:
        """Checks if the server process is currently running."""
        return self.process is not None and self.process.isalive()