import os
import sys
from bisect import insort
from collections import deque
from dataclasses import dataclass
from pathlib import Path

from humanize import naturalsize
from prettytable import PrettyTable


@dataclass
class File:
    name: str
    size: int
    full_path: str


def print_files_table(files: list[File]):
    # Printing tables: https://learnpython.com/blog/print-table-in-python/
    # Human readable file size: https://stackoverflow.com/a/15485265/8094047
    column_labels = ["Name", "Size", "Full path"]
    table = PrettyTable(column_labels, align="l")

    for file in files:
        table.add_row(
            [
                file.name,
                naturalsize(file.size, binary=True),
                Path(file.full_path).absolute(),
            ]
        )

    print(table)


def get_files_recursive_step(
    path: str, directories_queue: deque[str], files: list[File], n: int
):
    with os.scandir(path) as it:
        for entry in it:
            # Ignore directories and files that start with a dot
            if entry.name.startswith("."):
                continue
            # We also don't handle symbolic links for now
            if entry.is_file(follow_symlinks=False):
                file = File(
                    entry.name,
                    entry.stat(follow_symlinks=False).st_size,
                    entry.path,
                )
                insort(files, file, key=lambda file: file.size)
                if len(files) > n:
                    files.pop(0)
            elif entry.is_dir(follow_symlinks=False):
                directories_queue.append(entry.path)


def get_largest_files_recursive(path: str, n: int) -> list[File]:
    files: list[File] = []

    # We use a queue to recursively traverse the directory tree
    directories_queue: deque[str] = deque()
    directories_queue.append(path)

    while len(directories_queue) > 0:
        dirpath = directories_queue.popleft()
        try:
            get_files_recursive_step(dirpath, directories_queue, files, n)
        # I tried running the script in my home directory so I catch these errors
        except PermissionError:
            print(f"Permission denied for {dirpath}")
        except FileNotFoundError:
            print(f"File not found {dirpath}")
        except ProcessLookupError:
            print(f"Process lookup error for {dirpath}")
        except OSError:
            print(f"OS error for {dirpath}")

    return files[::-1]


def print_nlargest_files(path: str, n: int):
    largest_files = get_largest_files_recursive(path, n)
    print_files_table(largest_files)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print_nlargest_files(".", 10)
    elif len(sys.argv) == 2:
        print_nlargest_files(sys.argv[1], 10)
