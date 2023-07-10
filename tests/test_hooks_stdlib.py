"""Tests for some cx_Freeze.hooks."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from subprocess import check_output
from sysconfig import get_platform, get_python_version
from textwrap import dedent

try:
    from tomllib import load as toml_load
except ImportError:
    try:
        from setuptools.extern.tomli import load as toml_load
    except ImportError:
        from tomli import load as toml_load

PLATFORM = get_platform()
PYTHON_VERSION = get_python_version()
BUILD_EXE_DIR = f"build/exe.{PLATFORM}-{PYTHON_VERSION}"
FIXTURE_DIR = Path(__file__).resolve().parent
CX_FREEZE_DIR_STR = FIXTURE_DIR.parent.as_posix()


def create_sample(test_dir: Path, name: str) -> dict:
    """Create the sample in test_dir."""
    samples_toml = Path(__file__).with_suffix(".toml")
    if not samples_toml.exists():
        print(f"{samples_toml.name!r} not found", file=sys.stderr)
        sys.exit(1)
    with samples_toml.open("rb") as file:
        config = toml_load(file)
    test_data: dict = config[name]
    try:
        sources: dict = test_data["sources"]
    except KeyError:
        sys.exit(1)
    executables: list = test_data.get("executables")
    if executables is None:
        executables = [src for src in sources if src != "setup.py"]
        test_data["executables"] = executables
    if sources.get("setup.py") is None:
        executables_with_class = []
        for executable in executables:
            executables_with_class.append(f"Executable({executable!r})")
        sources["setup.py"] = dedent(
            f"""
            from cx_Freeze import Executable, setup
            setup(executables=[{", ".join(executables_with_class)}])
            """
        )
    for source, data in sources.items():
        source_path: Path = test_dir / source
        source_path.parent.mkdir(parents=True, exist_ok=True)
        source_path.write_text(data, encoding="utf-8")
    return test_data


def test_ssl(tmp_path: Path):
    """Test that the ssl is working correctly."""
    test_data = create_sample(tmp_path, "test_ssl")
    output = check_output(
        [
            sys.executable,
            "setup.py",
            "build_exe",
            "--silent",
            "--excludes=tkinter",
        ],
        text=True,
        cwd=os.fspath(tmp_path),
    )
    print(output)
    suffix = ".exe" if sys.platform == "win32" else ""
    executables: list = test_data["executables"]
    for name in executables:
        executable_name = Path(name).with_suffix(suffix).name
        executable = tmp_path / BUILD_EXE_DIR / executable_name
        assert executable.is_file()
        output = subprocess.check_output(
            [os.fspath(executable)], text=True, timeout=10
        )
        print(output)
        assert output.splitlines()[0] == "Hello from cx_Freeze"
        assert output.splitlines()[2] != ""
