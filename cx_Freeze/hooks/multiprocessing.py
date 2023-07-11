"""A collection of functions which are triggered automatically by finder when
multiprocessing package is included.
"""

from __future__ import annotations

import os
from textwrap import dedent

from cx_Freeze.finder import ModuleFinder
from cx_Freeze.module import Module


def load_multiprocessing(
    finder: ModuleFinder, module: Module  # noqa: ARG001
) -> None:
    """The forkserver method calls utilspawnv_passfds in ensure_running to
    pass a command line to python. In cx_Freeze the running executable
    is called, then we need to catch this and use exec function.
    For the spawn method there are a similar process to resource_tracker.

    Note: multiprocessing.freeze_support works only for windows, and
    multiprocessing.spawn.freeze_support works for all OS,
    so run it and disable the former.
    """
    if module.file.suffix == ".pyc":  # source unavailable
        return
    source = r"""
    # cx_Freeze patch start
    import os
    import sys

    import threading
    import multiprocessing
    import multiprocessing.spawn

    from subprocess import _args_from_interpreter_flags

    # Prevent `spawn` from trying to read `__main__` in from the main script
    multiprocessing.process.ORIGINAL_DIR = None

    def _freeze_support():
        # We want to catch the two processes that are spawned by the multiprocessing code:
        # - the semaphore tracker, which cleans up named semaphores in the `spawn` multiprocessing mode
        # - the fork server, which keeps track of worker processes in the `forkserver` mode.
        # Both of these processes are started by spawning a new copy of the running executable, passing it the flags
        # from `_args_from_interpreter_flags` and then "-c" and an import statement.
        # Look for those flags and the import statement, then `exec()` the code ourselves.

        if (
            len(sys.argv) >= 2 and sys.argv[-2] == '-c' and sys.argv[-1].startswith(
                ('from multiprocessing.resource_tracker import main', 'from multiprocessing.forkserver import main')
            ) and set(sys.argv[1:-2]) == set(_args_from_interpreter_flags())
        ):
            exec(sys.argv[-1])
            sys.exit()

        if multiprocessing.spawn.is_forking(sys.argv):
            kwds = {}
            for arg in sys.argv[2:]:
                name, value = arg.split('=')
                if value == 'None':
                    kwds[name] = None
                else:
                    kwds[name] = int(value)
            multiprocessing.spawn.spawn_main(**kwds)
            sys.exit()

    multiprocessing.freeze_support = multiprocessing.spawn.freeze_support = _freeze_support
    # cx_Freeze patch end
    """
    code_string = module.file.read_text(encoding="utf-8") + dedent(source)
    module.code = compile(code_string, os.fspath(module.file), "exec")
