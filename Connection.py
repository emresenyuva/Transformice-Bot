#!/usr/bin/env python
import socket, sys, time

import ByteStream

class new:
	def __init__(self, name):
		self.socket = None
		self.name = name
		self.fingerprint = 0

	def open_sock(self, host_name, port):
		try:
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		except:
			print("Connection (%s): socket can't be created." % self.name)
			sys.exit(0)

		sock.settimeout(3)

		host = socket.gethostbyname(host_name)
		if host == None:
			print("Connection (%s): host could not be resolved." % self.name)
			sys.exit(0)
		try:
			sock.connect((host, port))
		except socket.timeout:
			print("Connection (%s): connection timed out." % self.name)
			sys.exit(0)

		sock.settimeout(None)

		self.socket = sock

	def send(self, b):
		new_b = ByteStream.new()
		if b.length() < 0x100:
			new_b.write_byte(1)
			new_b.write_byte(b.length())
		else:
			new_b.write_byte(2)
			new_b.write_u16(b.length())
		new_b.write_byte(self.fingerprint)
		try:
			self.socket.send(new_b.to_string() + b.to_string())
			self.fingerprint = (self.fingerprint + 1) % 100
		except:
			pass
