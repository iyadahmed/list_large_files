import os
import sys
from collections import deque
from dataclasses import dataclass
from heapq import nlargest
from pathlib import Path

from humanize import naturalsize
from prettytable import PrettyTable

# Quote from Python docs on heapq.nlargest and heapq.nsmallest:
# The latter two functions perform best for smaller values of n.
# For larger values, it is more efficient to use the sorted() function.
# Also, when n==1, it is more efficient to use the built-in min() and max() functions.
# If repeated usage of these functions is required, consider turning the iterable into an actual heap.

# NOTE: maybe it is better for memory usage to not store all the files in a list
# but rather only keep record of top n largest files and replace them when a larger file is found
# like insertion sort or something


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
    path: str, directories_queue: deque[str], files: list[File]
):
    with os.scandir(path) as it:
        for entry in it:
            # Ignore directories and files that start with a dot
            if entry.name.startswith("."):
                continue
            # We also don't handle symbolic links for now
            if entry.is_file(follow_symlinks=False):
                files.append(
                    File(
                        entry.name,
                        entry.stat(follow_symlinks=False).st_size,
                        entry.path,
                    )
                )
            elif entry.is_dir(follow_symlinks=False):
                directories_queue.append(entry.path)


def get_files_recursive(path: str) -> list[File]:
    files: list[File] = []

    # We use a queue to recursively traverse the directory tree
    directories_queue: deque[str] = deque()
    directories_queue.append(path)

    while len(directories_queue) > 0:
        dirpath = directories_queue.popleft()
        try:
            get_files_recursive_step(dirpath, directories_queue, files)
        # I tried running the script in my home directory so I catch these errors
        except PermissionError:
            print(f"Permission denied for {dirpath}")
        except FileNotFoundError:
            print(f"File not found {dirpath}")
        except ProcessLookupError:
            print(f"Process lookup error for {dirpath}")
        except OSError:
            print(f"OS error for {dirpath}")

    return files


def print_nlargest_files(path: str, n: int):
    files = get_files_recursive(path)
    largest_files = nlargest(n, files, key=lambda file: file.size)
    print_files_table(largest_files)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print_nlargest_files(".", 10)
    elif len(sys.argv) == 2:
        print_nlargest_files(sys.argv[1], 10)
