#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Script based on:
# https://github.com/i3/i3status/blob/4d3344ab9cd68bad5faf4ed3dad185dfcacb1e3d/contrib/wrapper.py

import sys
import json
import subprocess

COLOR_RED = "#FF0000"
COLOR_YELLOW = "#FFFF00"


def print_line(message):
    """Non-buffered printing to stdout."""
    sys.stdout.write(message + '\n')
    sys.stdout.flush()


def read_line():
    """Interrupted respecting reader for stdin."""

    # try reading a line, removing any extra whitespace
    try:
        line = sys.stdin.readline().strip()
        # i3status sends EOF, or an empty line
        if not line:
            sys.exit(3)
        return line

    # exit on ctrl-c
    except KeyboardInterrupt:
        sys.exit()


def mem_used() -> dict:
    def process_max_mem_used() -> str:
        command = r"ps -o pid,user,%mem,command ax | sort -b -k3 -r| head -2 | tail -1"
        ps_command = subprocess.Popen(
            command, shell=True, stdout=subprocess.PIPE, text=True
        )
        stdout_data, _ = ps_command.communicate()
        pid, user, mem_perc, command, *_ = stdout_data.split()
        return f"pid={pid} user={user} %mem={mem_perc} command={command}..."

    free_command = subprocess.run(["free"], stdout=subprocess.PIPE, text=True)
    used = free_command.stdout.split()[8]
    total = free_command.stdout.split()[7]
    memory_used = round(float(used) / float(total) * 100.0)

    status = {"name": "mem_used", "full_text": f"mem u: {memory_used} %"}
    if 80 <= memory_used < 100:
        status.update({
            "full_text": f"process: {process_max_mem_used()} mem u: {memory_used} %",
            "color": COLOR_RED,
        })
    elif 70 <= memory_used < 80:
        status.update({
            "full_text": f"process: {process_max_mem_used()} mem u: {memory_used} %",
            "color": COLOR_YELLOW
        })

    return status


def add_custom_configuration():
    return [
        mem_used(),
    ]


if __name__ == '__main__':
    # Skip the first line which contains the version header.
    print_line(read_line())

    # The second line contains the start of the infinite array.
    print_line(read_line())

    while True:
        line, prefix = read_line(), ''
        # ignore comma at start of lines
        if line.startswith(','):
            line, prefix = line[1:], ','

        j = json.loads(line)
        for config in add_custom_configuration():
            j.insert(0, config)

        # and echo back new encoded json
        print_line(prefix + json.dumps(j))
