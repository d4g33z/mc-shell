import subprocess
import threading

from mcshell.constants import *

_paper_cmds  = [
    'mvrule keepInventory true brave_new_world',
    'mvmodify set gamemode creative brave_new_world',
    'mvmodify set animals false brave_new_world',
    'mvmodify set monsters false brave_new_world',
    'mvmodify set pvp false brave_new_world',
    'mvmodify set difficulty EASY',
    'mvmodify set color AQUA'

]

def execute_paper_server_in_thread():
    """
    Executes a paper server in a separate process.
    """

    command = ['java', '-Xms1G', '-Xmx2G', '-Dpaper.log-level=FATAL', '-jar', MC_PAPER_JAR_PATH ,'nogui']

    try:
        # Use Popen for more control over the process
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        if stdout:
            print(f"JAR stdout:\n{stdout.decode()}")
        if stderr:
            print(f"JAR stderr:\n{stderr.decode()}")

        if process.returncode != 0:
            print(f"JAR exited with error code: {process.returncode}")

    except FileNotFoundError:
        print("Error: Java or the specified JAR file not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

paper_server_thread = None
def start_local_paper_server():
    global paper_server_thread

    if paper_server_thread and paper_server_thread.is_alive():
        print("A local paper server is already running.")
        return

    paper_server_thread = threading.Thread(
        target=execute_paper_server_in_thread,
        daemon=True,
    )
    paper_server_thread.start()
    time.sleep(1) # Give the server a moment to start
    if paper_server_thread.is_alive():
        print(f"Paper server started in thread: {paper_server_thread.ident}")
    else:
        print("Error: Paper server thread failed to start.")

