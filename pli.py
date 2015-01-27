"""
PLI Communication Library
Designed for use with PLI Serial Interface Adaptor for PL Controllers
Copyright (C) 2012 Ace Internet Services Pty Ltd

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import socket
import time

READ_PROCESSOR_LOCATION  = 0x14
READ_EEPROM_LOCATION     = 0x48
WRITE_PROCESSOR_LOCATION = 0x98
WRITE_EEPROM_LOCATION    = 0xCA
LOOPBACK_TEST            = 0xBB
LOOPBACK_SUCCESS         = 0x80
RESPONSE_SUCCESS         = 0xC8

# some example data constants
BATTERY_VOLTAGE          = 0x32
BATTERY_TEMP             = 0x34

VOLTAGE_SETTING          = 0x2B

class PLI:

	def __init__(self, target, timeout=5, retries=3, retry_delay=1.0):
		"""	Constructor: opens connection to PLI controller.
			usage for TCP socket: PLI(('192.168.88.1', 26000))
			usage for serial:     PLI('/dev/ttyS0')
		"""

		self.retries = retries
		self.retry_delay = retry_delay

		if isinstance(target, (list, tuple)): # socket connection
			for res in socket.getaddrinfo(target[0], target[1], socket.AF_UNSPEC, socket.SOCK_STREAM):
				af, socktype, proto, canonname, sa = res
				try:
					s = socket.socket(af, socktype, proto)
				except socket.error, msg:
					s = None
					continue
				try:
					s.connect(sa)
				except socket.error, msg:
					s.close()
					s = None
					continue
				break
			if s is None:
				raise Exception('could not open socket')

			s.settimeout(timeout)

			self.comm = s

		elif isinstance(target, basestring): # file I/O based (tty) connection
			s = open(target, 'r+b')
			if s is None:
				raise Exception('could not open serial port')
			self.comm = s

		else:
			raise Exception('could not understand what you want to connect to')

	def destroy(self):
		"""	Close socket or file handle when destroying object.
		"""
		self.comm.close()

	def comm_write(self, data):
		"""	Wrapper to call correct write method depending on
			whether we are using a socket or file handle.
		"""
		if isinstance(self.comm, socket.socket): # socket
			self.comm.sendall(data)
		elif isinstance(self.comm, file): # file
			self.comm.write(data)

	def comm_read(self, bufsize=0):
		"""	Wrapper to call correct read method depending on
			whether we are using a socket or file handle.
		"""
		if isinstance(self.comm, socket.socket): # socket
			return self.comm.recv(bufsize)
		elif isinstance(self.comm, file): # file
			return self.comm.read(bufsize)

	def comm_call(self, command_code, address, write_data=0):
		"""	RPC call mechanism for serial interface.
			Expects three single-byte arguments, and concatenates them.
			Checks response is valid code. If not, retries up to three times.
		"""
		errors = []
		tries = 0
		while tries < self.retries:
			try:
				self.comm_write(''.join((
					chr(command_code  & 0xFF), # the "& 0xFF" ensures each arg is single byte
					chr(address       & 0xFF),
					chr(write_data    & 0xFF),
					chr(~command_code & 0xFF) # 1s compliment of first byte
				)))

				r = self.comm_read(2)

				if not r[0] == chr(RESPONSE_SUCCESS):
					raise InvalidResponseException(r[0])
				return r[1]
			except (socket.timeout, InvalidResponseException), e: # used to use "as e", but Python 2.4 choked
				if isinstance(e, InvalidResponseException):
					errors.append('%x' % ord(e.value))
				tries += 1
				time.sleep(self.retry_delay)
		raise InvalidResponseException('failed too many times, expected %x but got: %s' % (RESPONSE_SUCCESS, ', '.join(errors)))

	def get_value(self, index):
		"""	Wrapper to read from volatile RAM location.
		"""
		return ord(self.comm_call(READ_PROCESSOR_LOCATION, index))

	def get_eeprom(self, index):
		"""	Read from EEPROM (non-volatile) RAM location
		"""
		return ord(self.comm_call(READ_EEPROM_LOCATION, index))

	def set_eeprom(self, index, value):
		"""	Write to EEPROM (non-volatile) RAM location
		"""
		return ord(self.comm_call(WRITE_EEPROM_LOCATION, index, value))

	def loopback_test(self):
		self.comm_write(''.join((
			chr(LOOPBACK_TEST),
			chr(0),
			chr(0),
			chr(~LOOPBACK_TEST & 0xFF)
		)))
		return self.comm_read(1) == chr(LOOPBACK_SUCCESS)

class InvalidResponseException(Exception):
	"""	Used if a serial response returns an error or otherwise
		unexpected code.
		
		Originally inherited from BaseException, but due to
		Python 2.4 compatibility issues, changed to Exception.
	"""
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

