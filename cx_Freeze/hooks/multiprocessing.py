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
    import re
    import sys
    from multiprocessing.spawn import freeze_support

    if (  # What if we use the original code?
        len(sys.argv) >= 2 and sys.argv[-2] == '-c' and sys.argv[-1].startswith((
            'from multiprocessing.resource_tracker import main',
            'from multiprocessing.forkserver import main'
        )) and set(sys.argv[1:-2]) == set(util._args_from_interpreter_flags())
    ):
        exec(sys.argv[-1])
        sys.exit()
    freeze_support()
    freeze_support = lambda: None
    # cx_Freeze patch end
    """
    code_string = module.file.read_text(encoding="utf-8") + dedent(source)
    module.code = compile(code_string, os.fspath(module.file), "exec")
