#!/usr/bin/env python3
"""Temporary file used to initialize the package."""
import argparse
import glob
import os
import re
import shutil
from collections.abc import Callable, Sequence

SRC_FOLDERS = tuple([dirent for dirent in glob.glob("src*") if os.path.isdir(dirent)])
TEMP_NAME = "temporary-python-project"


def normalize(name: str) -> str:
    """Normalize a package name.

    Code taken from:
    https://packaging.python.org/en/latest/specifications/name-normalization/

    Parameters
    name : str
        The original package name.

    Returns:
    str
        The normalized package name.
    """
    return re.sub(r"[-_.]+", "_", name).lower()


def create_replacer(
    pattern: re.Pattern | str, replacement: str = ""
) -> Callable[[str], str]:
    """Create a replacer depending on the pattern."""
    if isinstance(pattern, str):

        def replacer(text: str) -> str:
            return text.replace(pattern, replacement)
    else:

        def replacer(text: str) -> str:
            return pattern.sub(replacement, text)

    return replacer


def update_file(file: str, pattern: re.Pattern | str, replacement: str = "") -> None:
    """Update the contents of a file."""
    with open(file) as w_fp:
        result = create_replacer(pattern=pattern, replacement=replacement)(
            w_fp.read()
        ).splitlines(keepends=True)
    with open(file, "w") as fp:
        fp.writelines(result)


def create_parser():
    """Create the parser for CLI arguments."""
    parser = argparse.ArgumentParser("Python template initializer.")
    parser.add_argument(
        "package-name",
        type=str,
        help="The name of the package to create.",
    )
    parser.add_argument(
        "--src",
        choices=SRC_FOLDERS,
        default=SRC_FOLDERS[0],
        help="The src folder to use. All others will be deleted.",
    )
    return parser


def main(args: Sequence[str] | None = None):
    """Update the package names."""
    values = vars(create_parser().parse_args(args))
    print(values)
    package_name = normalize(values["package-name"])
    with open("README.md", "w") as fp:
        fp.write(
            f"""# {TEMP_NAME}
"""
        )
    for file in (
        f"{values['src']}/__init__.py",
        "pyproject.toml",
        "README.md",
        "Makefile",
        ".github/workflows/qc-and-test.yaml",
    ):
        print(f"Updating '{file}'.")
        update_file(file, TEMP_NAME, package_name)
    for file in os.listdir(workflow_dir := ".github/workflows"):
        print(f"Updating '{file}'.")
        update_file(
            os.path.join(workflow_dir, file),
            re.compile(
                r"if: \${{github\.repository != 'mahdilamb\/python-template'}}\n\W*",
                re.MULTILINE | re.DOTALL,
            ),
        )
    print("Cleaning up...")
    if os.path.exists(package_name):
        print(f"'./{package_name}/' already exists...deleting!")
        shutil.rmtree(package_name)
    shutil.move(values["src"], package_name)
    for src in SRC_FOLDERS:
        if src == values["src"]:
            continue
        print(f"Deleting './{src}'.")
        shutil.rmtree(package_name)
    os.remove(__file__)


if __name__ == "__main__":
    main()
