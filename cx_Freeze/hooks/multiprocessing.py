"""A collection of functions which are triggered automatically by finder when
multiprocessing package is included.
"""

from __future__ import annotations

import os
from textwrap import dedent

from cx_Freeze._compat import IS_WINDOWS
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
    if IS_WINDOWS:  # patch is not needed
        return
    if module.file.suffix == ".pyc":  # source unavailable
        return
    source = r"""
    # cx_Freeze patch start
    import re
    import sys
    from multiprocessing.spawn import freeze_support

    if len(sys.argv) >= 2 and sys.argv[-2] == "-c":
        cmd = sys.argv[-1]
        if re.search(r"^from multiprocessing.* import main.*", cmd):
            exec(cmd)
            sys.exit()
    freeze_support()
    freeze_support = lambda: None
    # cx_Freeze patch end
    """
    code_string = module.file.read_text(encoding="utf-8") + dedent(source)
    module.code = compile(code_string, os.fspath(module.file), "exec")
