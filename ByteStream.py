# -*- coding: cp1254 -*-
import sys, btea
import Keys

class new:
	def __init__(self, array = None):
		self.array = []

		if array:
		    if type(array) is str:
		        self.array = [ord(c) for c in array]

	def write_byte(self, value):
		self.array.append(value)

	def write_u16(self, value):
		self.write_byte((value >> 8) & 0xff)
    		self.write_byte(value & 0xff)

	def write_u32(self, value):
		self.write_byte((value >> 24) & 0xff)
		self.write_byte((value >> 16) & 0xff)
		self.write_byte((value >> 8) & 0xff)
    		self.write_byte(value & 0xff)

	def write_str(self, string):
		self.write_u16(len(string))
		for k in string:
			self.write_byte(ord(k))

	def read_byte(self):
		if len(self.array) >= 1:
			val = self.array[0] & 0xff;
			del self.array[0]
			return val
		else:
			raise Exception("Index out of bounds")

	def read_boolean(self):
		if self.read_byte() > 0:
			return True
		else:
			return False

	def read_u16(self):
		return (self.read_byte() << 8) | self.read_byte()

	def read_u32(self):
		return (self.read_byte() << 24) | (self.read_byte() << 16) | (self.read_byte() << 8) | self.read_byte()

	def read_str(self):
		string = ""
		length = self.read_u16()
		for s in range(length):
			string += chr(self.read_byte())
		return string

	def block_cipher(self):
		if self.length() < 2:
			print("Block cipher attempted on empty byte_stream")
			sys.exit(0)
		while self.length() < 10:
			self.write_byte(0)

		pad_amt = (self.length() - 2) % 4
		if pad_amt:
			pad_amt = 4 - pad_amt
			for i in range(pad_amt):
				self.write_byte(0)
		num_chunks = (self.length() - 2) / 4
		chunks = []
		ccc = self.read_u16()
		for i in range(num_chunks):
			chunks.append(self.read_u32())
		btea.encode(chunks, num_chunks, Keys.IDENTIFICATION_KEY)
		b = new()
		b.write_u16(ccc);
		b.write_u16(num_chunks)
		for chunk in chunks:
			b.write_u32(chunk)
		self.array = b.array


	def xor_cipher(self, fingerprint):
		for i in range(2, len(self.array)):
			fingerprint = fingerprint + 1
			self.array[i] = (self.array[i]  ^ Keys.MSG_KEY[fingerprint % 20]) & 0xff

	def to_string(self):
		out = ""
		for b in self.array:
			out += chr(b)
		return out

	def avalible(self):
		return self.array > 0

	def length(self):
		return len(self.array)

	def skip(self, p):
		self.array = self.array[p:]

	def loc(self, s, e):
		out = ""
		for b in self.array[s:e]:
			out += chr(b)
		return out
