#!/usr/bin/env python
import threading, sys, time, os, hashlib, base64
sys.dont_write_bytecode = True

import ByteStream, Connection, Settings, Keys, Token

class Bot:
	def __init__(bot):
		bot.running = True
		bot.fingerprint = 0
		bot.id = 0
		bot.room = ""
		bot.runtime = time.time()

		bot.main_conn = Connection.new("Main")
		bot.bulle_conn = Connection.new("Bulle")

	def handle_packet(bot, conn, b):
		if b.length() < 2: return 0
		ccc = b.read_u16()
		if ccc == Token.SWITCH_BULLE:
			bot.id = b.read_u32()
			host = b.read_str()
			bot.bulle_conn.open_sock(host, 5555)

			b = ByteStream.new()
			b.write_u16(Token.SWITCH_BULLE)
			b.write_u32(bot.id)
			bot.bulle_conn.send(b)

		if ccc == Token.HANDSHAKE_OK:
			players_online = b.read_u32()
			conn.fingerprint = b.read_byte()
			community = b.read_str()
			country = b.read_str()
			login_xor = b.read_u32()
			print("Connected %s.%s :: %i online players" %
				   (country, community, players_online))

			threading.Timer(10, bot.heartbeat_task).start()

			b = ByteStream.new()
			b.write_u16(Token.SET_COMMUNITY)
			b.write_byte(Settings.COMMUNITY); b.write_byte(0)
			bot.main_conn.send(b)

			b = ByteStream.new()
			b.write_u16(Token.OS_INFO)
			b.write_str("en")
			b.write_str("Linux")
			b.write_str("LNX 29,0,0,140")
			b.write_byte(0);
			bot.main_conn.send(b)

			b = ByteStream.new()
			b.write_u16(Token.LOGIN)
			b.write_str(Settings.USERNAME.lower().capitalize())
			b.write_str(base64.b64encode(hashlib.sha256(hashlib.sha256(Settings.PASSWORD).hexdigest() + 'f71aa6de8f1776a8039d32b8a156b2a93edd439dc5ddce56d3b7a4054a0d08b0'.decode('hex')).digest()))
			b.write_str(Settings.FLASH_URL)
			b.write_str(Settings.ROOM_NAME)
			b.write_u32(Keys.LOGIN_KEY ^ login_xor)
			b.block_cipher()
			b.write_byte(0)
			bot.main_conn.send(b)

		if ccc == Token.SET_KEY_OFFSET:
			conn.fingerprint = b.read_byte()

		if ccc == Token.ROOM_JOIN:
			b.read_byte()
			bot.room = b.read_str()
			print("Joined room : %s" % bot.room)
			threading.Thread(target = bot.terminal).start()

		if ccc == Token.PLAYER_CHAT:
			player_id, username, language, message = b.read_u32(), b.read_str(), b.read_byte(), b.read_str()

		if ccc == Token.LOGIN_OK:
			forum_id, username = b.read_u32(), b.read_str()
			print("Connected with name : %s" % username)

		if ccc == Token.NEW_MAP:
			pass

	def heartbeat_task(bot):
		b = ByteStream.new()
		b.write_u16(Token.HEARTBEAT)
		bot.main_conn.send(b)
		bot.bulle_conn.send(b)
		if bot.running:
			threading.Timer(10, bot.heartbeat_task).start()

	def change_room(bot, room_name):
		b = ByteStream.new()
		b.write_u16(Token.ROOM_JOIN_REQUEST)
		b.write_byte(0xff)
		b.write_str(room_name)
		b.write_byte(0)
		bot.main_conn.send(b)

	def send_chat(bot, message, conn):
		b = ByteStream.new()
		b.write_u16(Token.PLAYER_CHAT)
		b.write_str(message)
		b.xor_cipher(conn.fingerprint)
		conn.send(b)

	def handshake(bot):
		b = ByteStream.new()
		b.write_u16(Token.HANDSHAKE)
		b.write_u16(Keys.HANDSHAKE_NUMBER)
		b.write_str(Keys.HANDSHAKE_STRING)
		b.write_str("Desktop")
		b.write_str("-")
		b.write_u32(0x00001FBD)
		b.write_str("")
		b.write_str("86bd7a7ce36bec7aad43d51cb47e30594716d972320ef4322b7d88a85904f0ed")
		b.write_str("A=t&SA=t&SV=t&EV=t&MP3=t&AE=t&VE=t&ACC=t&PR=t&SP=f&SB=f&DEB=f&V=LNX 29,0,0,140&M=Adobe Linux&R=1920x1080&COL=color&AR=1.0&OS=Linux&ARCH=x86&L=en&IME=t&PR32=t&PR64=t&LS=en-US&PT=Desktop&AVD=f&LFD=f&WD=f&TLS=t&ML=5.1&DP=72")
		b.write_u32(0)
		b.write_u32(0x00006257)
		b.write_str("")
		bot.main_conn.send(b)

	def check_conn(bot, conn):
		if conn.socket == None:
			return 0
		ret = conn.socket.recv(1)
		if len(ret) > 0:
			int_t = ord(ret)
			length = 0
			if int_t == 1:
				length = ord(conn.socket.recv(1))
			elif int_t == 2:
				length = (ord(conn.socket.recv(1)) << 8) | ord(conn.socket.recv(1))
			else:
				length = 0
			pack = conn.socket.recv(length)
			bot.handle_packet(conn, ByteStream.new(pack))

	def terminal(bot):
		while 1:
			command = raw_input('>> ')
			if command == 'exit':
				if bot.bulle_conn.socket != None:
					bot.bulle_conn.socket.close()
				bot.main_conn.socket.close()
				os._exit(1)

			if command.startswith('room '):
				room_name = ' '.join(command.split()[1:])
				bot.change_room(room_name)

			if command.startswith('msg '):
				message = ' '.join(command.split()[1:])
				bot.send_chat(message, bot.bulle_conn)

	def start(bot):
		bot.main_conn.open_sock(Settings.HOST, Settings.PORT)
		bot.handshake()
		while bot.running:
			if bot.bulle_conn.socket != None:
				bot.check_conn(bot.bulle_conn)
			else:
				bot.check_conn(bot.main_conn)

main = Bot()
try:
	main.start()
except KeyboardInterrupt:
	if main.bulle_conn.socket != None:
		main.bulle_conn.socket.close()
	main.main_conn.socket.close()
	os._exit(1)
