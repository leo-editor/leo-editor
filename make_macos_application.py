#!/usr/bin/env python3
# @+leo-ver=5-thin
# @+node:axk.20260702120000.1: * @file ../../make_macos_application.py
# @@first
"""Create Leo.app, a macOS launcher for a bundled Leo source tree."""

from __future__ import annotations

import argparse
import os
import plistlib
import shutil
import stat
import struct
import subprocess
import sys
import tempfile
from pathlib import Path


APP_NAME = "Leo.app"
EXECUTABLE_NAME = "leo-wrapper"
ICON_NAME = "AppIcon.icns"
DEFAULT_APP_PATH = Path("/Applications") / APP_NAME
SOURCE_ROOT = Path(__file__).resolve().parent
DEFAULT_ICON_SOURCE = SOURCE_ROOT / "leo" / "Icons" / "leoapp_macos.png"
DEFAULT_SUPPORT_DIR = Path.home() / "Library" / "Application Support" / "Leo"
DEFAULT_VENV_PATH = DEFAULT_SUPPORT_DIR / "venv"
RESOURCE_SOURCE_DIR = "leo-editor"

INFO_PLIST: dict[str, object] = {
    "CFBundleDevelopmentRegion": "en",
    "CFBundleDisplayName": "Leo",
    "CFBundleExecutable": EXECUTABLE_NAME,
    "CFBundleIconFile": "AppIcon",
    "CFBundleIdentifier": "local.leo.wrapper",
    "CFBundleInfoDictionaryVersion": "6.0",
    "CFBundleName": "Leo",
    "CFBundlePackageType": "APPL",
    "CFBundleShortVersionString": "1.0",
    "CFBundleVersion": "1",
    "LSApplicationCategoryType": "public.app-category.developer-tools",
    "LSMinimumSystemVersion": "12.0",
    "NSHighResolutionCapable": True,
}


def make_wrapper(venv_path: Path) -> str:
    wrapper = """#!/bin/zsh

set -euo pipefail

export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

SCRIPT_DIR="${0:A:h}"
CONTENTS_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
RESOURCES_DIR="$CONTENTS_DIR/Resources"
LEO_HOME="$RESOURCES_DIR/leo-editor"
LEO_VENV="__LEO_VENV__"
LEO_PYTHON="$LEO_VENV/bin/python3"
typeset -a site_paths
site_paths=("$LEO_VENV"/lib/python*/site-packages(N))

if [[ ! -x "$LEO_PYTHON" ]]; then
  osascript -e 'display alert "Leo runtime not found" message "Run make_macos_application.py to create the uv-managed Leo environment." as critical'
  exit 127
fi

if [[ ! -f "$LEO_HOME/launchLeo.py" ]]; then
  osascript -e 'display alert "Leo source not found" message "The bundled Leo source tree is missing launchLeo.py." as critical'
  exit 127
fi

if (( ${#site_paths} == 0 )); then
  osascript -e 'display alert "Leo dependencies not found" message "The uv-managed Leo virtual environment is missing site-packages." as critical'
  exit 127
fi

export PYTHONNOUSERSITE=1
export PYTHONPATH="$LEO_HOME:${site_paths[1]}${PYTHONPATH:+:$PYTHONPATH}"

cd "$HOME"
export PWD="$HOME"
unset OLDPWD
exec "$LEO_PYTHON" "$LEO_HOME/launchLeo.py" "$@"
"""
    return wrapper.replace("__LEO_VENV__", str(venv_path))


def copy_preserved_icon(app_path: Path, temp_dir: Path) -> Path | None:
    icon_path = app_path / "Contents" / "Resources" / ICON_NAME
    if not icon_path.exists():
        return None
    preserved_icon = temp_dir / ICON_NAME
    shutil.copy2(icon_path, preserved_icon)
    return preserved_icon


def make_icon(source: Path, target: Path) -> None:
    if not source.exists():
        raise FileNotFoundError(f"Icon source does not exist: {source}")
    if source.suffix.lower() == ".icns":
        shutil.copy2(source, target)
        return
    if shutil.which("sips") is None:
        raise RuntimeError("Creating an .icns file requires macOS sips")

    with tempfile.TemporaryDirectory(prefix="leo-icon-") as icon_dir_name:
        icon_dir = Path(icon_dir_name)
        chunks: list[bytes] = []
        for icon_type, pixels in (
            ("icp4", 16),
            ("icp5", 32),
            ("icp6", 64),
            ("ic07", 128),
            ("ic08", 256),
            ("ic09", 512),
            ("ic10", 1024),
        ):
            png_path = icon_dir / f"{pixels}.png"
            subprocess.run(
                ["sips", "-z", str(pixels), str(pixels), str(source), "--out", str(png_path)],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            png = png_path.read_bytes()
            chunks.append(icon_type.encode("ascii") + struct.pack(">I", len(png) + 8) + png)
        body = b"".join(chunks)
        target.write_bytes(b"icns" + struct.pack(">I", len(body) + 8) + body)


def copy_source_tree(source_root: Path, target: Path) -> None:
    ignore = shutil.ignore_patterns(
        ".git",
        ".jj",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".venv",
        "__pycache__",
        "build",
        "dist",
        "*.egg-info",
        "*.pyc",
    )
    shutil.copytree(source_root, target, ignore=ignore)


def make_read_only(path: Path) -> None:
    for child in path.rglob("*"):
        mode = child.stat().st_mode
        if child.is_dir():
            child.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        child.chmod(mode & ~stat.S_IWUSR & ~stat.S_IWGRP & ~stat.S_IWOTH)
    mode = path.stat().st_mode
    path.chmod(mode & ~stat.S_IWUSR & ~stat.S_IWGRP & ~stat.S_IWOTH)


def remove_tree(path: Path) -> None:
    for child in path.rglob("*"):
        if child.is_dir():
            child.chmod(child.stat().st_mode | stat.S_IRWXU)
        else:
            child.chmod(child.stat().st_mode | stat.S_IWUSR)
    path.chmod(path.stat().st_mode | stat.S_IRWXU)
    shutil.rmtree(path)


def install_uv_venv(venv_path: Path, source_root: Path, python: str | None) -> None:
    uv = shutil.which("uv")
    if uv is None:
        raise RuntimeError("uv is required to create the Leo virtual environment")

    requirements = source_root / "requirements.txt"
    if not requirements.exists():
        raise FileNotFoundError(f"Requirements file does not exist: {requirements}")

    venv_path.parent.mkdir(parents=True, exist_ok=True)
    venv_cmd = [uv, "venv", str(venv_path)]
    if python:
        venv_cmd.extend(["--python", python])
    subprocess.run(venv_cmd, check=True)

    python_path = venv_path / "bin" / "python3"
    subprocess.run(
        [uv, "pip", "install", "--python", str(python_path), "-r", str(requirements)],
        check=True,
    )


def write_app(
    app_path: Path,
    source_root: Path,
    venv_path: Path,
    icon_source: Path | None,
    preserve_existing_icon: bool,
    skip_venv_install: bool,
    python: str | None,
    dry_run: bool,
) -> None:
    contents_dir = app_path / "Contents"
    macos_dir = contents_dir / "MacOS"
    resources_dir = contents_dir / "Resources"

    if dry_run:
        print(f"Would remove: {app_path}")
        print(f"Would create: {macos_dir}")
        print(f"Would create: {resources_dir}")
        print(f"Would copy Leo source from: {source_root}")
        print("Would make copied Leo source read-only")
        if skip_venv_install:
            print(f"Would use existing uv-managed Python environment: {venv_path}")
        else:
            print(f"Would create/update uv-managed Python environment: {venv_path}")
        print(f"Would write icon from: {icon_source or DEFAULT_ICON_SOURCE}")
        return

    if not skip_venv_install:
        install_uv_venv(venv_path, source_root, python)

    with tempfile.TemporaryDirectory(prefix="leo-app-") as temp_dir_name:
        temp_dir = Path(temp_dir_name)
        staged_app = temp_dir / APP_NAME
        staged_contents = staged_app / "Contents"
        staged_macos = staged_contents / "MacOS"
        staged_resources = staged_contents / "Resources"
        preserved_icon = copy_preserved_icon(app_path, temp_dir) if preserve_existing_icon else None
        resolved_icon_source = icon_source or preserved_icon or DEFAULT_ICON_SOURCE

        staged_macos.mkdir(parents=True)
        staged_resources.mkdir(parents=True)

        with (staged_contents / "Info.plist").open("wb") as f:
            plistlib.dump(INFO_PLIST, f, sort_keys=False)

        wrapper_path = staged_macos / EXECUTABLE_NAME
        wrapper_path.write_text(make_wrapper(venv_path), encoding="utf-8")
        wrapper_path.chmod(wrapper_path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

        bundled_source = staged_resources / RESOURCE_SOURCE_DIR
        copy_source_tree(source_root, bundled_source)
        make_read_only(bundled_source)

        target_icon = staged_resources / ICON_NAME
        make_icon(resolved_icon_source, target_icon)

        if app_path.exists():
            remove_tree(app_path)
        shutil.move(str(staged_app), app_path)
        os.utime(app_path)

    print(f"Created {app_path}")
    print(f"Bundled read-only Leo source: {source_root}")
    print(f"uv-managed Python environment: {venv_path}")
    print(f"Icon source: {resolved_icon_source}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--app-path",
        type=Path,
        default=DEFAULT_APP_PATH,
        help=f"Application bundle to replace (default: {DEFAULT_APP_PATH})",
    )
    parser.add_argument(
        "--source-root",
        type=Path,
        default=SOURCE_ROOT,
        help=f"Leo checkout to bundle (default: {SOURCE_ROOT})",
    )
    parser.add_argument(
        "--venv-path",
        type=Path,
        default=DEFAULT_VENV_PATH,
        help=f"uv-managed Python venv to create/use (default: {DEFAULT_VENV_PATH})",
    )
    parser.add_argument(
        "--python", help="Python version or executable to pass to 'uv venv --python'."
    )
    parser.add_argument(
        "--skip-venv-install", action="store_true", help="Do not create/update the uv-managed venv."
    )
    parser.add_argument(
        "--icon-source",
        type=Path,
        help=f"Image or .icns file to use for AppIcon.icns (default: {DEFAULT_ICON_SOURCE})",
    )
    parser.add_argument(
        "--preserve-existing-icon",
        action="store_true",
        help="Reuse the existing app icon when --icon-source is not provided.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Show what would be changed.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source_root = args.source_root.expanduser().resolve()
    venv_path = args.venv_path.expanduser().resolve()
    try:
        write_app(
            args.app_path,
            source_root,
            venv_path,
            args.icon_source,
            args.preserve_existing_icon,
            args.skip_venv_install,
            args.python,
            args.dry_run,
        )
    except PermissionError as e:
        print(f"Permission denied: {e}", file=sys.stderr)
        print(
            "Try running this script with privileges that can write to /Applications.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
# @-leo
