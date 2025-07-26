from mcshell.mcblockly import process_entities,process_materials, build_final_toolbox

import click
class SpecialHelpOrderBase(click.Group):
    pass

# see https://stackoverflow.com/questions/47972638/how-can-i-define-the-order-of-click-sub-commands-in-help
class SpecialHelpOrder(SpecialHelpOrderBase):
    def __init__(self, *args, **kwargs):
        self.help_priorities = {}
        super(SpecialHelpOrder, self).__init__(*args, **kwargs)

    def get_help(self, ctx):
        self.list_commands = self.list_commands_for_help
        return super(SpecialHelpOrder, self).get_help(ctx)

    def list_commands_for_help(self, ctx):
        """reorder the list of commands when listing the help"""
        commands = super(SpecialHelpOrder, self).list_commands(ctx)
        return (c[1] for c in sorted(
            (self.help_priorities.get(command, 1), command)
            for command in commands))

    def command(self, *args, **kwargs):
        """Behaves the same as `click.Group.command()` except capture
        a priority for listing command names in help.
        """
        # if not priority is specified put it at the bottom
        help_priority = kwargs.pop('help_priority', 1000)
        help_priorities = self.help_priorities

        def decorator(f):
            cmd = super(SpecialHelpOrder, self).command(*args, **kwargs)(f)
            help_priorities[cmd.name] = help_priority
            return cmd

        return decorator


from traitlets.config import Config
# configure the ipython shell
def initialize_config():
    c = Config()
    c.TerminalIPythonApp.display_banner = False
    c.InteractiveShellApp.extensions = [
        'rich'
    ]
    c.InteractiveShellApp.exec_lines = [
        '%gui asyncio',
        '%load_ext autoreload',
        '%autoreload 2',
        # requires pickleshare
        "%store -r",
        'pdb',
    ]
    c.Application.log_level = 0
    return c

@click.group(cls=SpecialHelpOrder)
def cli():
    """
    mcshell: A Minecraft Server Interface
    """

@cli.command(
    help_priority=25,
    cls=click.Command,
    help="""
start an ipython session with mcshell magics
""")
def start():
    c = initialize_config()

    c.InteractiveShellApp.exec_lines += [
        'from mcshell import *',
    ]

    c.InteractiveShellApp.extensions += [
        'mcshell',
    ]

    import IPython
    IPython.start_ipython(config=c, argv=[])
