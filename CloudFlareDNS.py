#!/usr/bin/env python3

import nmcli
import argparse

parser = argparse.ArgumentParser(prog="cf", description="Simple CloudFlare DNS Tool")

parser.add_argument("command", help="command to issue", choices=["enable", "disable", "toggle", "status"], nargs="?")
parser.add_argument("-s", "--silent", help="silences all printing", action="store_true")
parser.add_argument("-c", "--color", help="Highlight display", action="store_true")
parser.add_argument("-i", "--indent", help="Indent display", action="store_true")
args = parser.parse_args()

enabled = False
ignoreAuto = "no"

# TODO: Fetch this and not need it as a const
networkName = "Mines-Legacy"

def load():
	global enabled, ignoreAuto
	con = nmcli.connection.show(networkName)
	ignoreAuto = con["ipv4.ignore-auto-dns"]
	i = 1
	DNS = []
	while f"IP4.DNS[{i}]" in con:
		DNS.append(con[f"IP4.DNS[{i}]"])
		i += 1

	enabled = '1.1.1.1' in DNS

def downUpCon():
	try:
		nmcli.connection.down(networkName)
	except nmcli._exception.NotExistException:
		pass
	nmcli.connection.up(networkName)

def enable():
	global enabled
	load()
	if enabled:
		if not args.silent:
			print("Already enabled, exiting")
		exit()
	nmcli.connection.modify(networkName, {"ipv4.ignore-auto-dns": "yes"})
	nmcli.connection.modify(networkName, {"ipv4.dns": "1.1.1.1 1.0.0.1"})
	downUpCon()

def disable():
	global enabled
	load()
	if not enabled:
		if not args.silent:
			print("Already disabled, exiting")
		exit()
	nmcli.connection.modify(networkName, {"ipv4.ignore-auto-dns": "no"})
	nmcli.connection.modify(networkName, {"ipv4.dns": ""})
	downUpCon()

if args.command == "enable":
	enable()
if args.command == "disable":
	disable()
if args.command == "toggle":
	if enabled:
		disable()
	else:
		enable()

if not args.silent:
	nmcli.disable_use_sudo()
	load()
	indentChar = " " if args.indent else ""
	if args.color:
		ignoreAutoColor = '\033[32myes\033[0m' if (ignoreAuto == 'yes') else '\033[31mno\033[0m'
		print(f"{indentChar}Ignore DHCP DNS:    {ignoreAutoColor}")
		enabledColor = '\033[32myes\033[0m' if enabled else '\033[31mno\033[31m'
		print(f"{indentChar}CloudFlare enabled: {enabledColor}")
	else:
		print(f"{indentChar}Ignore DHCP DNS:    {ignoreAuto}")
		print(f"{indentChar}CloudFlare enabled: {'yes' if enabled else 'no'}")

