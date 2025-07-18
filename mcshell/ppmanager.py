import subprocess
import threading

from mcshell.constants import *

class PaperServerManager:
    """Manages the lifecycle of a single Paper server subprocess."""

    def __init__(self, world_name: str, world_directory: pathlib.Path):
        self.world_name = world_name
        self.world_directory = world_directory
        self.process: Optional[subprocess.Popen,None] = None
        self.thread: Optional[threading.Thread,None]  = None

    def _execute_in_thread(self):
        """
        The target function for the server thread. It starts the Paper server
        and waits for it to complete.
        """
        world_manifest = json.load(self.world_directory.joinpath('world_manifest.json').open('br'))
        # Command to run the server from within its specific world directory
        command = [
            'java',
            '-Xms2G', '-Xmx2G', # Example memory settings
            '-jar', str(self.world_directory.parent.joinpath(world_manifest.get('server_jar_path'))),
            'nogui'
        ]

        print(f"Starting Paper server for world '{self.world_name}'...")
        print(f"  > Directory: {self.world_directory}")
        print(f"  > Command: {' '.join(command)}")

        try:
            # Use Popen to run the JAR as a non-blocking subprocess.
            # We set the current working directory to the world's directory.
            self.process = subprocess.Popen(
                command,
                cwd=self.world_directory,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True # Decode stdout/stderr as text
            )

            # You can optionally log the server's output in real-time
            # For now, we just wait for it to exit.
            self.process.wait()

        except FileNotFoundError:
            print("Error: 'java' command not found. Is Java installed and in your PATH?")
        except Exception as e:
            print(f"An error occurred while running the Paper server: {e}")
        finally:
            print(f"Paper server for world '{self.world_name}' has stopped.")

    def start(self):
        """Starts the Paper server in a new background daemon thread."""
        if self.is_alive():
            print(f"Server for world '{self.world_name}' is already running.")
            return

        self.thread = threading.Thread(target=self._execute_in_thread, daemon=True)
        self.thread.start()
        time.sleep(5) # Give the server a moment to start up and bind to ports

        if not self.is_alive():
            print(f"Error: Failed to start the server for world '{self.world_name}'.")

    def stop(self):
        """Stops the running Paper server process gracefully."""
        if not self.is_alive():
            print(f"Server for world '{self.world_name}' is not running.")
            return

        print(f"Sending 'stop' command to Paper server for '{self.world_name}'...")
        if self.process:
            try:
                # Send the 'stop' command to the server's stdin
                self.process.communicate(input='stop\n', timeout=30)
            except subprocess.TimeoutExpired:
                print("Server did not stop gracefully. Terminating process.")
                self.process.terminate()
            except Exception as e:
                print(f"An error occurred while stopping the server: {e}")
                self.process.kill()

        # Wait for the thread to finish
        self.thread.join(timeout=5)

    def is_alive(self) -> bool:
        """Checks if the server process is currently running."""
        return self.process is not None and self.process.poll() is None