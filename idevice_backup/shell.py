"""
gnome-extensions-cli
"""
import os
import shlex
import shutil
import signal
from pathlib import Path
from tempfile import TemporaryDirectory

import pexpect
from shellingham import detect_shell

SOURCE_COMMAND = {
    "fish": "source",
    "csh": "source",
    "tcsh": "source",
    "nu": "source",
    "bash": ".",
}


def spawn_shell(folder: Path, ps1_prefix: str | None = None) -> int:
    with TemporaryDirectory() as tmp:
        source_env = Path(tmp) / ".env"
        if ps1_prefix is not None:
            source_env.write_text(f'PS1="({ps1_prefix}) $PS1"')
        # spawn a new shell
        shell_name, shell_path = detect_shell(os.getpid())
        terminal = shutil.get_terminal_size()
        subshell = pexpect.spawn(
            shell_path,
            ["-i"],
            dimensions=(terminal.lines, terminal.columns),
            cwd=str(folder.absolute()),
        )
        if shell_name in ["zsh", "nu"]:
            subshell.setecho(False)
            if shell_name == "zsh":
                # Under ZSH the source command should be invoked in zsh's bash emulator
                subshell.sendline(f"emulate bash -c '. {shlex.quote(str(source_env))}'")
        else:
            subshell.sendline(
                f"{SOURCE_COMMAND.get(shell_name, '.')} {shlex.quote(str(source_env))}"
            )

        def resize(*args, **kwargs) -> None:
            terminal = shutil.get_terminal_size()
            subshell.setwinsize(terminal.lines, terminal.columns)

        signal.signal(signal.SIGWINCH, resize)

        # interact with the new shell.
        subshell.interact()
        subshell.close()
