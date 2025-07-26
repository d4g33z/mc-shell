# MC-Shell: A Minecraft Power Development Environment 

Welcome to `mc-shell`! This project provides an interactive environment for creating, debugging, and using "powers" in Minecraft. It combines a powerful command-line shell with a visual block-based editor and a touch-friendly control panel.

This guide will walk you through installing the software, managing your own Minecraft worlds, and using the tools to bring your creations to life.

## Quick Start

This guide will get you running in just a few minutes. Each step is linked to a more detailed section below.

1.  **[Install the Software](#installation)**:
    ```bash
    [coming soon via pip!]
    ```
2.  **[Enter the Shell](#entering-the-shell)**:
    ```bash
    mcshell start
    ```
3.  **[Create Your First World](#creating-and-listing-worlds)**:
    ```bash
    %pp_create_world my_first_world
    ```
4.  **[Start Your World](#starting-and-stopping-worlds)**:
    ```bash
    %pp_start_world my_first_world
    ```
5.  **[Use the Editor](#using-the-editor)**: Open a browser and go to `http://localhost:5001`.
6.  **[Exit Cleanly](#exiting-the-shell)**: Type `exit` or hit `Ctrl-D` in the shell to stop your world and the application server.

---

## Getting Started

### Installation

Before you begin, you will need a few things installed on your system (Linux, macOS, or Windows Subsystem for Linux):
* **Python** (version 3.9 or higher)

Once the prerequisites are met, run the following commands in your terminal to download and install the project and all its dependencies.

```bash
[coming soon via pip!]
````

### Running and Updating

To run the application, use the following command from the `mc-shell` directory:

```bash
mcshell start
```

### Entering the Shell

Running the application will drop you into `mc-shell`, an enhanced IPython terminal. From here, you can manage your Minecraft worlds and the `mc-ed` application using special "magic commands" that start with a `%` symbol.

-----

##  Managing Your Worlds (The "Atomic Multi-verse")

This section covers all the `%pp_` commands for managing your personal Paper server instances.

### Creating and Listing Worlds

To create a new, self-contained world, use the `%pp_create_world` command. This will create a new folder in your home directory (`~/mc-worlds`), download the appropriate Paper server, and set up all the necessary configuration files. The current default version (which the client must match) is `1.21.4`.
```ipython
%pp_create_world my_creative_build --version=1.21.4
```

To see a list of all the worlds you have created, use the `%pp_list_worlds` command.

### Starting and Stopping Worlds

The main command to start a session is `%pp_start_world`. This launches the specified Paper server in the background and starts the `mc-ed` application server, which provides the Editor and Control Panel UIs.

This command ensures only one world is active at a time. If you start a new world, it will automatically stop your previous session.

```ipython
%pp_start_world my_creative_build
```

To manually stop the current session (both the Paper server and the app server), use `%pp_stop_world`.

### Deleting Worlds

To permanently delete a world and all its files, use the `%pp_delete_world` command. You will be asked for confirmation before any files are removed.

```ipython
%pp_delete_world my_old_world
```

### Joining Worlds

This section covers how to connect to a running server. The `%mc_login` magic configures your shell to talk to a specific server, while `%mc_invite_player` allows you to send your connection details to a friend so they can join you.

### Exiting the Shell

When you are finished, you can exit the shell by typing `exit()` or pressing `Ctrl+D`. This will automatically trigger a clean shutdown of any running world and the application server.

-----

## Using the Tools

This section focuses on the two main graphical interfaces, which are available in your browser once a world is started.

### Using the Editor

The Editor is a powerful visual environment for creating "powers." You can access it at `http://localhost:5001`.

The interface consists of two main panels: the **Power Library** on the left, which lists your saved powers, and the main **Workspace** on the right. The workspace contains the **Blockly editor** for visually composing programs and a **live Python code preview** that updates as you work.

To create a functional power, you must follow the "Debug-to-Define" workflow:

1.  Create a **function definition** block (e.g., `def BuildTower(height)`).
2.  Create a **function call** block as a "test harness" and connect blocks with the correct types to its inputs (e.g., a `math_number` block for `height`).
3.  Click the **"Execute (Debug)"** button. This runs the code in-game and "type-stamps" your power's parameters with the correct types.
4.  Click **"Save Power As..."** to save this newly defined power to your library, ready to be used by the Control Panel.

### Using the Control

The Control Panel is a touch-friendly UI for executing your saved powers in-game. Access it at `http://localhost:5001/control`.

The interface has two modes:

  * **Run Mode:** The main grid displays your power "widgets." If a power has parameters, the widget will have interactive controls like sliders or pickers. Simply set the parameters and click "Execute."
  * **Edit Mode:** Click "Edit Layout" to customize your grid. You can open a library of all your saved powers, add them as new widgets to your grid, and drag-and-drop them to arrange your layout.
