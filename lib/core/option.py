#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
import sys

from gevent.queue import Queue
from lib.controller.bruter import loadConf
from lib.core.common import parseTarget, outputscreen
from lib.core.data import conf


def initOptions(args):
    EngineRegister(args)
    BruterRegister(args)
    TargetRegister(args)


def EngineRegister(args):
    conf.engine_mode = "coroutine"

    if not isinstance(args.thread_num, int) or args.thread_num < 1 or args.thread_num > 200:
        outputscreen.warning("[*] Invalid input in [-t] (range: 1..200). Using default: 30")
        conf.thread_num = 30
    else:
        conf.thread_num = args.thread_num


def BruterRegister(args):
    # gán debug flag (bool)
    conf.debug = bool(getattr(args, "debug", False))

    if getattr(args, "load_config_file", False):
        loadConf()
    else:
        outputscreen.error("[+] Feature not ready. Please use -lcf/--load-config-file to specify a config file.")
        sys.exit(1)


def TargetRegister(args):
    outputscreen.warning("[*] Initialize targets...")

    # Initialize target queue
    conf.target = Queue()

    target_input = getattr(args, "target_input", None)
    if target_input:
        try:
            targets = parseTarget(target_input)
        except Exception as e:
            outputscreen.error(
                "Invalid input in [-i]. Example:\n"
                "  -i [http://]target.com\n"
                "  -i 192.168.1.1[/24]\n"
                "  -i 192.168.1.1-192.168.1.100"
            )
            if conf.debug:
                outputscreen.error(f"[debug] parseTarget error: {e!r}")
            sys.exit(1)

        if len(targets) > 100_000:
            outputscreen.warning(f"[*] Loading {len(targets)} targets. Maybe it's too much, continue? [y/N]")
            try:
                ans = input().strip()
            except EOFError:
                ans = ""
            if ans not in ("Y", "y", "yes", "YES", "Yes"):
                outputscreen.warning("[-] User quit!")
                sys.exit(1)

        outputscreen.success(f"[+] Load targets from: {target_input}")
        for t in targets:
            conf.target.put(t)
        conf.target_nums = conf.target.qsize()

    elif getattr(args, "target_file", None):
        target_file = args.target_file
        if not os.path.isfile(target_file):
            outputscreen.error(f"[-] Target file not found: {target_file}")
            sys.exit(1)

        outputscreen.success(f"[+] Load targets from: {target_file}")
        try:
            with open(target_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        parsed = parseTarget(line)
                    except Exception as e:
                        if conf.debug:
                            outputscreen.error(f"[debug] parseTarget failed for line '{line}': {e!r}")
                        continue
                    for item in parsed:
                        conf.target.put(item)
        except Exception as e:
            outputscreen.error(f"[-] Failed to read target file: {e}")
            sys.exit(1)

        conf.target_nums = conf.target.qsize()

    if conf.target.qsize() == 0:
        outputscreen.error("[!] No targets found. Please load targets with [-i | -iF]")
        sys.exit(1)
