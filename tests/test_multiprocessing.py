"""Tests for multiprocessing."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from subprocess import check_output
from sysconfig import get_platform, get_python_version

from generate_samples import create_package

PLATFORM = get_platform()
PYTHON_VERSION = get_python_version()
BUILD_EXE_DIR = f"build/exe.{PLATFORM}-{PYTHON_VERSION}"

SOURCE = """\
sample1.py
    import multiprocessing

    def foo(q):
        q.put('hello')

    if __name__ == '__main__':
        print(locals())
        multiprocessing.freeze_support()
        multiprocessing.set_start_method('spawn')
        q = multiprocessing.SimpleQueue()
        p = multiprocessing.Process(target=foo, args=(q,))
        p.start()
        print(q.get())
        p.join()
sample2.py
    if __name__ ==  "__main__":
        import multiprocessing
        multiprocessing.freeze_support()
        multiprocessing.set_start_method('spawn')
        mgr = multiprocessing.Manager()
        # main process will use more memory (easier to find in device mgr)
        var = [1] * 10000000
        print("before creating dict")
        mgr_dict = mgr.dict({'test': var})
        print("after creating dict")
setup.py
    from cx_Freeze import Executable, setup
    setup(
        name="test_multiprocessing",
        version="0.1",
        description="Sample for test with cx_Freeze",
        executables=[Executable("sample1.py"), Executable("sample2.py")],
        options={
            "build_exe": {
                "excludes": ["tkinter"],
                "silent": True,
            }
        }
    )
"""


# @pytest.mark.skipif(sys.platform != "win32", reason="Windows tests")
def test_multiprocessing_1(tmp_path: Path):
    """Provides test cases for multiprocessing."""
    create_package(tmp_path, SOURCE)
    output = check_output(
        [sys.executable, "setup.py", "build_exe"],
        text=True,
        cwd=os.fspath(tmp_path),
    )
    print(output)
    suffix = ".exe" if sys.platform == "win32" else ""
    executable = tmp_path / BUILD_EXE_DIR / f"sample1{suffix}"
    assert executable.is_file()
    # pytest.fail()
    output = check_output(
        [os.fspath(executable)], text=True, timeout=10, cwd=os.fspath(tmp_path)
    )
    print(output)
    assert output.splitlines()[-1] == "hello"


def test_multiprocessing_2(tmp_path: Path):
    """Provides test cases for multiprocessing."""
    create_package(tmp_path, SOURCE)
    output = check_output(
        [sys.executable, "setup.py", "build_exe"],
        text=True,
        cwd=os.fspath(tmp_path),
    )
    print(output)
    suffix = ".exe" if sys.platform == "win32" else ""
    executable = tmp_path / BUILD_EXE_DIR / f"sample2{suffix}"
    assert executable.is_file()
    # pytest.fail()
    output = check_output(
        [os.fspath(executable)], text=True, timeout=10, cwd=os.fspath(tmp_path)
    )
    print(output)
    assert output.splitlines()[-1] == "after creating dict"
