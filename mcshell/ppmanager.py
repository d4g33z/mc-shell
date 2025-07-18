import pexpect
import threading
import time
from pathlib import Path
import sys # Needed for logging
from typing import Optional
import json

class PaperServerManager:
    """Manages the lifecycle of a single Paper server subprocess using pexpect."""

    def __init__(self, world_name: str, world_directory: Path):
        self.world_name = world_name
        self.world_directory = world_directory
        self.process: Optional[pexpect.spawn , None] = None
        self.thread: Optional[threading.Thread , None] = None

    def _execute_server(self):
        """
        The main execution function. Starts the Paper server and logs its
        output in real-time without blocking the parent thread.
        """
        # command = f"java -Xms2G -Xmx2G -jar {self.jar_path} nogui"
        #
        # print(f"Starting Paper server for world '{self.world_name}'...")
        # print(f"  > Directory: {self.world_directory}")

        world_manifest = json.load(self.world_directory.joinpath('world_manifest.json').open('br'))
        # Command to run the server from within its specific world directory
        command = ' '.join([
            'java',
            '-Xms2G', '-Xmx2G', # Example memory settings
            '-jar', str(self.world_directory.parent.joinpath(world_manifest.get('server_jar_path'))),
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

            # --- THIS IS THE FIX ---
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
            # --- END OF FIX ---

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