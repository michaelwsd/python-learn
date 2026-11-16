#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "rich>=15.0.0",
# ]
# ///

import shutil 
from rich.console import Console
from rich.table import Table

def main() -> None:
    usage = shutil.disk_usage("/")
    percent_used = usage.used / usage.total * 100 
    color = "red" if percent_used > 80 else "green"
    used_cell = cell = f"[{color}]{percent_used:.1f}%[/{color}]"

    table = Table(title="Disk Usage")
    table.add_column("Used")
    table.add_row(used_cell)

    Console().print(table)


if __name__ == "__main__":
    main()
