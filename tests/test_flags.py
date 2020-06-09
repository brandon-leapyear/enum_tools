# -*- coding: utf-8 -*-

# stdlib
import sys
import threading
import unittest
from collections import OrderedDict
from unittest import TestCase

# 3rd party
from aenum import auto  # type: ignore

# this package
from better_enum import Enum, Flag, IntFlag

pyver = float('%s.%s' % sys.version_info[:2])


class TestFlag(TestCase):
	"""Tests of the Flags."""

	class Perm(Flag):
		R, W, X = 4, 2, 1

	class Color(Flag):
		BLACK = 0
		RED = 1
		GREEN = 2
		BLUE = 4
		PURPLE = RED | BLUE

	class Open(Flag):
		RO = 0
		WO = 1
		RW = 2
		AC = 3
		CE = 1 << 19

	def test_membership(self):
		Color = self.Color
		Open = self.Open
		self.assertRaises(TypeError, lambda: 'BLACK' in Color)
		self.assertRaises(TypeError, lambda: 'RO' in Open)
		self.assertTrue(Color.BLACK in Color)
		self.assertTrue(Open.RO in Open)
		self.assertFalse(Color.BLACK in Open)
		self.assertFalse(Open.RO in Color)
		self.assertRaises(TypeError, lambda: 0 in Color)
		self.assertRaises(TypeError, lambda: 0 in Open)

	def test_member_contains(self):
		Color = self.Color
		self.assertRaises(TypeError, lambda: 'test' in Color.BLUE)
		self.assertRaises(TypeError, lambda: 2 in Color.BLUE)
		self.assertTrue(Color.BLUE in Color.BLUE)
		self.assertTrue(Color.BLUE in Color['RED|GREEN|BLUE'])

	def test_str(self):
		Perm = self.Perm
		self.assertEqual(str(Perm.R), 'Perm.R')
		self.assertEqual(str(Perm.W), 'Perm.W')
		self.assertEqual(str(Perm.X), 'Perm.X')
		self.assertEqual(str(Perm.R | Perm.W), 'Perm.R|W')
		self.assertEqual(str(Perm.R | Perm.W | Perm.X), 'Perm.R|W|X')
		self.assertEqual(str(Perm(0)), 'Perm.0')
		self.assertEqual(str(~Perm.R), 'Perm.W|X')
		self.assertEqual(str(~Perm.W), 'Perm.R|X')
		self.assertEqual(str(~Perm.X), 'Perm.R|W')
		self.assertEqual(str(~(Perm.R | Perm.W)), 'Perm.X')
		self.assertEqual(str(~(Perm.R | Perm.W | Perm.X)), 'Perm.0')
		self.assertEqual(str(Perm(~0)), 'Perm.R|W|X')

		Open = self.Open
		self.assertEqual(str(Open.RO), 'Open.RO')
		self.assertEqual(str(Open.WO), 'Open.WO')
		self.assertEqual(str(Open.AC), 'Open.AC')
		self.assertEqual(str(Open.RO | Open.CE), 'Open.CE')
		self.assertEqual(str(Open.WO | Open.CE), 'Open.CE|WO')
		self.assertEqual(str(~Open.RO), 'Open.CE|AC|RW|WO')
		self.assertEqual(str(~Open.WO), 'Open.CE|RW')
		self.assertEqual(str(~Open.AC), 'Open.CE')
		self.assertEqual(str(~(Open.RO | Open.CE)), 'Open.AC')
		self.assertEqual(str(~(Open.WO | Open.CE)), 'Open.RW')

	def test_repr(self):
		Perm = self.Perm
		self.assertEqual(repr(Perm.R), '<Perm.R: 4>')
		self.assertEqual(repr(Perm.W), '<Perm.W: 2>')
		self.assertEqual(repr(Perm.X), '<Perm.X: 1>')
		self.assertEqual(repr(Perm.R | Perm.W), '<Perm.R|W: 6>')
		self.assertEqual(repr(Perm.R | Perm.W | Perm.X), '<Perm.R|W|X: 7>')
		self.assertEqual(repr(Perm(0)), '<Perm.0: 0>')
		self.assertEqual(repr(~Perm.R), '<Perm.W|X: 3>')
		self.assertEqual(repr(~Perm.W), '<Perm.R|X: 5>')
		self.assertEqual(repr(~Perm.X), '<Perm.R|W: 6>')
		self.assertEqual(repr(~(Perm.R | Perm.W)), '<Perm.X: 1>')
		self.assertEqual(repr(~(Perm.R | Perm.W | Perm.X)), '<Perm.0: 0>')
		self.assertEqual(repr(Perm(~0)), '<Perm.R|W|X: 7>')

		Open = self.Open
		self.assertEqual(repr(Open.RO), '<Open.RO: 0>')
		self.assertEqual(repr(Open.WO), '<Open.WO: 1>')
		self.assertEqual(repr(Open.AC), '<Open.AC: 3>')
		self.assertEqual(repr(Open.RO | Open.CE), '<Open.CE: 524288>')
		self.assertEqual(repr(Open.WO | Open.CE), '<Open.CE|WO: 524289>')
		self.assertEqual(repr(~Open.RO), '<Open.CE|AC|RW|WO: 524291>')
		self.assertEqual(repr(~Open.WO), '<Open.CE|RW: 524290>')
		self.assertEqual(repr(~Open.AC), '<Open.CE: 524288>')
		self.assertEqual(repr(~(Open.RO | Open.CE)), '<Open.AC: 3>')
		self.assertEqual(repr(~(Open.WO | Open.CE)), '<Open.RW: 2>')

	def test_name_lookup(self):
		Color = self.Color
		self.assertTrue(Color.RED is Color['RED'])
		self.assertTrue(Color.RED | Color.GREEN is Color['RED|GREEN'])
		self.assertTrue(Color.PURPLE is Color['RED|BLUE'])

	def test_or(self):
		Perm = self.Perm
		for i in Perm:
			for j in Perm:
				self.assertEqual((i | j), Perm(i.value | j.value))
				self.assertEqual((i | j).value, i.value | j.value)
				self.assertIs(type(i | j), Perm)
		for i in Perm:
			self.assertIs(i | i, i)
		Open = self.Open
		self.assertIs(Open.RO | Open.CE, Open.CE)

	def test_and(self):
		Perm = self.Perm
		RW = Perm.R | Perm.W
		RX = Perm.R | Perm.X
		WX = Perm.W | Perm.X
		RWX = Perm.R | Perm.W | Perm.X
		values = list(Perm) + [RW, RX, WX, RWX, Perm(0)]
		for i in values:
			for j in values:
				self.assertEqual((i & j).value, i.value & j.value)
				self.assertIs(type(i & j), Perm)
		for i in Perm:
			self.assertIs(i & i, i)
			self.assertIs(i & RWX, i)
			self.assertIs(RWX & i, i)
		Open = self.Open
		self.assertIs(Open.RO & Open.CE, Open.RO)

	def test_xor(self):
		Perm = self.Perm
		for i in Perm:
			for j in Perm:
				self.assertEqual((i ^ j).value, i.value ^ j.value)
				self.assertIs(type(i ^ j), Perm)
		for i in Perm:
			self.assertIs(i ^ Perm(0), i)
			self.assertIs(Perm(0) ^ i, i)
		Open = self.Open
		self.assertIs(Open.RO ^ Open.CE, Open.CE)
		self.assertIs(Open.CE ^ Open.CE, Open.RO)

	def test_invert(self):
		Perm = self.Perm
		RW = Perm.R | Perm.W
		RX = Perm.R | Perm.X
		WX = Perm.W | Perm.X
		RWX = Perm.R | Perm.W | Perm.X
		values = list(Perm) + [RW, RX, WX, RWX, Perm(0)]
		for i in values:
			self.assertIs(type(~i), Perm)
			self.assertEqual(~~i, i)
		for i in Perm:
			self.assertIs(~~i, i)
		Open = self.Open
		self.assertIs(Open.WO & ~Open.WO, Open.RO)
		self.assertIs((Open.WO | Open.CE) & ~Open.WO, Open.CE)

	def test_bool(self):
		Perm = self.Perm
		for f in Perm:
			self.assertTrue(f)
		Open = self.Open
		for f in Open:
			self.assertEqual(bool(f.value), bool(f))

	def test_iteration(self):
		C = self.Color
		self.assertEqual(list(C), [C.BLACK, C.RED, C.GREEN, C.BLUE, C.PURPLE])

	def test_member_iteration(self):
		C = self.Color
		self.assertEqual(list(C.BLACK), [])
		self.assertEqual(list(C.RED), [C.RED])
		self.assertEqual(list(C.PURPLE), [C.BLUE, C.RED])

	def test_programatic_function_string(self):
		Perm = Flag('Perm', 'R W X')
		lst = list(Perm)
		self.assertEqual(len(lst), len(Perm))
		self.assertEqual(len(Perm), 3, Perm)
		self.assertEqual(lst, [Perm.R, Perm.W, Perm.X])
		for i, n in enumerate('R W X'.split()):
			v = 1 << i
			e = Perm(v)
			self.assertEqual(e.value, v)
			self.assertEqual(type(e.value), int)
			self.assertEqual(e.name, n)
			self.assertIn(e, Perm)
			self.assertIs(type(e), Perm)

	def test_programatic_function_string_with_start(self):
		Perm = Flag('Perm', 'R W X', start=8)
		lst = list(Perm)
		self.assertEqual(len(lst), len(Perm))
		self.assertEqual(len(Perm), 3, Perm)
		self.assertEqual(lst, [Perm.R, Perm.W, Perm.X])
		for i, n in enumerate('R W X'.split()):
			v = 8 << i
			e = Perm(v)
			self.assertEqual(e.value, v)
			self.assertEqual(type(e.value), int)
			self.assertEqual(e.name, n)
			self.assertIn(e, Perm)
			self.assertIs(type(e), Perm)

	def test_programatic_function_string_list(self):
		Perm = Flag('Perm', ['R', 'W', 'X'])
		lst = list(Perm)
		self.assertEqual(len(lst), len(Perm))
		self.assertEqual(len(Perm), 3, Perm)
		self.assertEqual(lst, [Perm.R, Perm.W, Perm.X])
		for i, n in enumerate('R W X'.split()):
			v = 1 << i
			e = Perm(v)
			self.assertEqual(e.value, v)
			self.assertEqual(type(e.value), int)
			self.assertEqual(e.name, n)
			self.assertIn(e, Perm)
			self.assertIs(type(e), Perm)

	def test_programatic_function_iterable(self):
		Perm = Flag('Perm', (('R', 2), ('W', 8), ('X', 32)))
		lst = list(Perm)
		self.assertEqual(len(lst), len(Perm))
		self.assertEqual(len(Perm), 3, Perm)
		self.assertEqual(lst, [Perm.R, Perm.W, Perm.X])
		for i, n in enumerate('R W X'.split()):
			v = 1 << (2 * i + 1)
			e = Perm(v)
			self.assertEqual(e.value, v)
			self.assertEqual(type(e.value), int)
			self.assertEqual(e.name, n)
			self.assertIn(e, Perm)
			self.assertIs(type(e), Perm)

	def test_programatic_function_from_dict(self):
		Perm = Flag('Perm', OrderedDict((('R', 2), ('W', 8), ('X', 32))))
		lst = list(Perm)
		self.assertEqual(len(lst), len(Perm))
		self.assertEqual(len(Perm), 3, Perm)
		self.assertEqual(lst, [Perm.R, Perm.W, Perm.X])
		for i, n in enumerate('R W X'.split()):
			v = 1 << (2 * i + 1)
			e = Perm(v)
			self.assertEqual(e.value, v)
			self.assertEqual(type(e.value), int)
			self.assertEqual(e.name, n)
			self.assertIn(e, Perm)
			self.assertIs(type(e), Perm)

	def test_containment(self):
		Perm = self.Perm
		R, W, X = Perm
		RW = R | W
		RX = R | X
		WX = W | X
		RWX = R | W | X
		self.assertTrue(R in RW)
		self.assertTrue(R in RX)
		self.assertTrue(R in RWX)
		self.assertTrue(W in RW)
		self.assertTrue(W in WX)
		self.assertTrue(W in RWX)
		self.assertTrue(X in RX)
		self.assertTrue(X in WX)
		self.assertTrue(X in RWX)
		self.assertFalse(R in WX)
		self.assertFalse(W in RX)
		self.assertFalse(X in RW)

	def test_auto_number(self):

		class Color(Flag):
			_order_ = 'red blue green'
			red = auto()
			blue = auto()
			green = auto()

		self.assertEqual(list(Color), [Color.red, Color.blue, Color.green])
		self.assertEqual(Color.red.value, 1)
		self.assertEqual(Color.blue.value, 2)
		self.assertEqual(Color.green.value, 4)

	#
	# def test_auto_number_garbage(self):
	# 	with self.assertRaisesRegex(TypeError, 'Invalid Flag value: .not an int.'):
	#
	# 		class Color(Flag):
	# 			_order_ = 'red blue'
	# 			red = 'not an int'
	# 			blue = auto()

	# def test_auto_w_pending(self):
	#
	# 	class Required(Flag):
	# 		_order_ = 'NONE TO_S FROM_S BOTH'
	# 		NONE = 0
	# 		TO_S = auto()
	# 		FROM_S = auto()
	# 		BOTH = TO_S | FROM_S
	#
	# 	self.assertEqual(Required.TO_S.value, 1)
	# 	self.assertEqual(Required.FROM_S.value, 2)
	# 	self.assertEqual(Required.BOTH.value, 3)

	# def test_cascading_failure(self):
	#
	# 	class Bizarre(Flag):
	# 		c = 3
	# 		d = 4
	# 		f = 6
	#
	# 	# Bizarre.c | Bizarre.d
	# 	self.assertRaisesRegex(ValueError, "5 is not a valid Bizarre", Bizarre, 5)
	# 	self.assertRaisesRegex(ValueError, "5 is not a valid Bizarre", Bizarre, 5)
	# 	self.assertRaisesRegex(ValueError, "2 is not a valid Bizarre", Bizarre, 2)
	# 	self.assertRaisesRegex(ValueError, "2 is not a valid Bizarre", Bizarre, 2)
	# 	self.assertRaisesRegex(ValueError, "1 is not a valid Bizarre", Bizarre, 1)
	# 	self.assertRaisesRegex(ValueError, "1 is not a valid Bizarre", Bizarre, 1)

	def test_duplicate_auto(self):

		class Dupes(Enum):
			_order_ = 'first second third'
			first = primero = auto()
			second = auto()
			third = auto()

		self.assertEqual([Dupes.first, Dupes.second, Dupes.third], list(Dupes))

	def test_bizarre(self):

		class Bizarre(Flag):
			b = 3
			c = 4
			d = 6

		self.assertEqual(repr(Bizarre(7)), '<Bizarre.d|c|b: 7>')

	@unittest.skipUnless(threading, 'Threading required for this test.')
	def test_unique_composite(self):
		# override __eq__ to be identity only
		class TestFlag(Flag):
			_order_ = 'one two three four five six seven eight'
			one = auto()
			two = auto()
			three = auto()
			four = auto()
			five = auto()
			six = auto()
			seven = auto()
			eight = auto()

			def __eq__(self, other):
				return self is other

			def __hash__(self):
				return hash(self._value_)

		# have multiple threads competing to complete the composite members
		seen = set()
		failed = [False]

		def cycle_enum():
			# nonlocal failed
			try:
				for i in range(256):
					seen.add(TestFlag(i))
			except Exception:
				failed[0] = True

		threads = [threading.Thread(target=cycle_enum) for _ in range(8)]
		for t in threads:
			t.start()
		for t in threads:
			t.join()
		# check that only 248 members were created (8 were created originally)
		self.assertFalse(failed[0], 'at least one thread failed while creating composite members')
		self.assertEqual(256, len(seen), 'too many composite members created')

	#
	# def test_ignore_with_autovalue_and_property(self):
	#
	# 	class Color(str, Flag):
	# 		_order_ = 'FG_Black FG_Red FG_Green FG_Blue BG_Yellow BG_Magenta BG_Cyan BG_White'
	# 		_settings_ = AutoValue
	#
	# 		def __new__(cls, value, code):
	# 			str_value = '\x1b[%sm' % code
	# 			obj = str.__new__(cls, str_value)
	# 			obj._value_ = value
	# 			obj.code = code
	# 			return obj
	#
	# 		@staticmethod
	# 		def _generate_next_value_(name, start, count, values, *args, **kwds):
	# 			return (2**count, ) + args
	#
	# 		@classmethod
	# 		def _create_pseudo_member_(cls, value):
	# 			pseudo_member = cls._value2member_map_.get(value, None)
	# 			if pseudo_member is None:
	# 				# calculate the code
	# 				members, _ = _decompose(cls, value)
	# 				code = ';'.join(m.code for m in members)
	# 				pseudo_member = super(Color, cls)._create_pseudo_member_(value, code)
	# 			return pseudo_member
	#
	# 		#
	# 		# # FOREGROUND - 30s  BACKGROUND - 40s:
	# 		FG_Black = '30'  # ESC [ 30 m      # black
	# 		FG_Red = '31'  # ESC [ 31 m      # red
	# 		FG_Green = '32'  # ESC [ 32 m      # green
	# 		FG_Blue = '34'  # ESC [ 34 m      # blue
	# 		#
	# 		BG_Yellow = '43'  # ESC [ 33 m      # yellow
	# 		BG_Magenta = '45'  # ESC [ 35 m      # magenta
	# 		BG_Cyan = '46'  # ESC [ 36 m      # cyan
	# 		BG_White = '47'  # ESC [ 37 m      # white
	#
	# 	# if we got here, we're good


# 	def test_subclass(self):
#
# 		class Color(str, Flag):
# 			_order_ = 'FG_Black FG_Red FG_Green FG_Blue BG_Yellow BG_Magenta BG_Cyan BG_White'
# 			_settings_ = AutoValue
#
# 			def __new__(cls, value, code):
# 				str_value = '\x1b[%sm' % code
# 				obj = str.__new__(cls, str_value)
# 				obj._value_ = value
# 				obj.code = code
# 				return obj
#
# 			@staticmethod
# 			def _generate_next_value_(name, start, count, values, *args, **kwds):
# 				return (2**count, ) + args
#
# 			@classmethod
# 			def _create_pseudo_member_(cls, value):
# 				pseudo_member = cls._value2member_map_.get(value, None)
# 				if pseudo_member is None:
# 					# calculate the code
# 					members, _ = _decompose(cls, value)
# 					code = ';'.join(m.code for m in members)
# 					pseudo_member = super(Color, cls)._create_pseudo_member_(value, code)
# 				return pseudo_member
#
# 			#
# 			# # FOREGROUND - 30s  BACKGROUND - 40s:
# 			FG_Black = '30'  # ESC [ 30 m      # black
# 			FG_Red = '31'  # ESC [ 31 m      # red
# 			FG_Green = '32'  # ESC [ 32 m      # green
# 			FG_Blue = '34'  # ESC [ 34 m      # blue
# 			#
# 			BG_Yellow = '43'  # ESC [ 33 m      # yellow
# 			BG_Magenta = '45'  # ESC [ 35 m      # magenta
# 			BG_Cyan = '46'  # ESC [ 36 m      # cyan
# 			BG_White = '47'  # ESC [ 37 m      # white
#
# 		self.assertTrue(isinstance(Color.FG_Black, Color))
# 		self.assertTrue(isinstance(Color.FG_Black, str))
# 		self.assertEqual(Color.FG_Black, '\x1b[30m')
# 		self.assertEqual(Color.FG_Black.code, '30')
#
# 	def test_sub_subclass_1(self):
#
# 		class StrFlag(str, Flag):
# 			_settings_ = AutoValue
#
# 			def __new__(cls, value, code):
# 				str_value = '\x1b[%sm' % code
# 				obj = str.__new__(cls, str_value)
# 				obj._value_ = value
# 				obj.code = code
# 				return obj
#
# 			@classmethod
# 			def _create_pseudo_member_(cls, value):
# 				pseudo_member = cls._value2member_map_.get(value, None)
# 				if pseudo_member is None:
# 					# calculate the code
# 					members, _ = _decompose(cls, value)
# 					code = ';'.join(m.code for m in members)
# 					pseudo_member = super(Color, cls)._create_pseudo_member_(value, code)
# 				return pseudo_member
#
# 			#
# 		class Color(StrFlag):
# 			_order_ = 'FG_Black FG_Red FG_Green FG_Blue BG_Yellow BG_Magenta BG_Cyan BG_White'
# 			# # FOREGROUND - 30s  BACKGROUND - 40s:
# 			FG_Black = '30'  # ESC [ 30 m      # black
# 			FG_Red = '31'  # ESC [ 31 m      # red
# 			FG_Green = '32'  # ESC [ 32 m      # green
# 			FG_Blue = '34'  # ESC [ 34 m      # blue
# 			#
# 			BG_Yellow = '43'  # ESC [ 33 m      # yellow
# 			BG_Magenta = '45'  # ESC [ 35 m      # magenta
# 			BG_Cyan = '46'  # ESC [ 36 m      # cyan
# 			BG_White = '47'  # ESC [ 37 m      # white
#
# 		self.assertTrue(isinstance(Color.FG_Black, Color))
# 		self.assertTrue(isinstance(Color.FG_Black, str))
# 		self.assertEqual(Color.FG_Black, '\x1b[30m')
# 		self.assertEqual(Color.FG_Black.code, '30')
#
# 	def test_sub_subclass_2(self):
#
# 		class StrFlag(str, Flag):
# 			_settings_ = AutoValue
#
# 			@staticmethod
# 			def _generate_next_value_(name, start, count, values, *args, **kwds):
# 				return (2**count, ) + args
#
# 			@classmethod
# 			def _create_pseudo_member_(cls, value):
# 				pseudo_member = cls._value2member_map_.get(value, None)
# 				if pseudo_member is None:
# 					# calculate the code
# 					members, _ = _decompose(cls, value)
# 					code = ';'.join(m.code for m in members)
# 					pseudo_member = super(Color, cls)._create_pseudo_member_(value, code)
# 				return pseudo_member
#
# 			#
# 		class Color(StrFlag):
# 			_order_ = 'FG_Black FG_Red FG_Green FG_Blue BG_Yellow BG_Magenta BG_Cyan BG_White'
#
# 			def __new__(cls, value, code):
# 				str_value = '\x1b[%sm' % code
# 				obj = str.__new__(cls, str_value)
# 				obj._value_ = value
# 				obj.code = code
# 				return obj
# 				# # FOREGROUND - 30s  BACKGROUND - 40s:
#
# 			FG_Black = '30'  # ESC [ 30 m      # black
# 			FG_Red = '31'  # ESC [ 31 m      # red
# 			FG_Green = '32'  # ESC [ 32 m      # green
# 			FG_Blue = '34'  # ESC [ 34 m      # blue
# 			#
# 			BG_Yellow = '43'  # ESC [ 33 m      # yellow
# 			BG_Magenta = '45'  # ESC [ 35 m      # magenta
# 			BG_Cyan = '46'  # ESC [ 36 m      # cyan
# 			BG_White = '47'  # ESC [ 37 m      # white
#
# 		self.assertTrue(isinstance(Color.FG_Black, Color))
# 		self.assertTrue(isinstance(Color.FG_Black, str))
# 		self.assertEqual(Color.FG_Black, '\x1b[30m')
# 		self.assertEqual(Color.FG_Black.code, '30')
#
# 	def test_sub_subclass_3(self):
#
# 		class StrFlag(str, Flag):
#
# 			def __new__(cls, value, code):
# 				str_value = '\x1b[%sm' % code
# 				obj = str.__new__(cls, str_value)
# 				obj._value_ = value
# 				obj.code = code
# 				return obj
#
# 			@classmethod
# 			def _create_pseudo_member_(cls, value):
# 				pseudo_member = cls._value2member_map_.get(value, None)
# 				if pseudo_member is None:
# 					# calculate the code
# 					members, _ = _decompose(cls, value)
# 					code = ';'.join(m.code for m in members)
# 					pseudo_member = super(Color, cls)._create_pseudo_member_(value, code)
# 				return pseudo_member
#
# 			#
# 		class Color(StrFlag):
# 			_settings_ = AutoValue
# 			_order_ = 'FG_Black FG_Red FG_Green FG_Blue BG_Yellow BG_Magenta BG_Cyan BG_White'
# 			# # FOREGROUND - 30s  BACKGROUND - 40s:
# 			FG_Black = '30'  # ESC [ 30 m      # black
# 			FG_Red = '31'  # ESC [ 31 m      # red
# 			FG_Green = '32'  # ESC [ 32 m      # green
# 			FG_Blue = '34'  # ESC [ 34 m      # blue
# 			#
# 			BG_Yellow = '43'  # ESC [ 33 m      # yellow
# 			BG_Magenta = '45'  # ESC [ 35 m      # magenta
# 			BG_Cyan = '46'  # ESC [ 36 m      # cyan
# 			BG_White = '47'  # ESC [ 37 m      # white
#
# 		self.assertTrue(isinstance(Color.FG_Black, Color))
# 		self.assertTrue(isinstance(Color.FG_Black, str))
# 		self.assertEqual(Color.FG_Black, '\x1b[30m')
# 		self.assertEqual(Color.FG_Black.code, '30')
#
# 	def test_sub_subclass_4(self):
#
# 		class StrFlag(str, Flag):
#
# 			def __new__(cls, value, code):
# 				str_value = '\x1b[%sm' % code
# 				obj = str.__new__(cls, str_value)
# 				obj._value_ = value
# 				obj.code = code
# 				return obj
#
# 			@classmethod
# 			def _create_pseudo_member_values_(cls, members, *values):
# 				code = ';'.join(m.code for m in members)
# 				return values + (code, )
#
# 			#
# 		class Color(StrFlag):
# 			_settings_ = AutoValue
# 			_order_ = 'FG_Black FG_Red FG_Green FG_Blue BG_Yellow BG_Magenta BG_Cyan BG_White'
# 			# # FOREGROUND - 30s  BACKGROUND - 40s:
# 			FG_Black = '30'  # ESC [ 30 m      # black
# 			FG_Red = '31'  # ESC [ 31 m      # red
# 			FG_Green = '32'  # ESC [ 32 m      # green
# 			FG_Blue = '34'  # ESC [ 34 m      # blue
# 			#
# 			BG_Yellow = '43'  # ESC [ 33 m      # yellow
# 			BG_Magenta = '45'  # ESC [ 35 m      # magenta
# 			BG_Cyan = '46'  # ESC [ 36 m      # cyan
# 			BG_White = '47'  # ESC [ 37 m      # white
#
# 			#
# 			def __repr__(self):
# 				if self._name_ is not None:
# 					return '<%s.%s>' % (self.__class__.__name__, self._name_)
# 				else:
# 					return '<%s: %s>' % (self.__class__.__name__, '|'.join([m.name for m in Flag.__iter__(self)]))
#
# 		self.assertTrue(isinstance(Color.FG_Black, Color))
# 		self.assertTrue(isinstance(Color.FG_Black, str))
# 		self.assertEqual(Color.FG_Black, '\x1b[30m')
# 		self.assertEqual(Color.FG_Black.code, '30')
# 		colors = Color.BG_Magenta | Color.FG_Black
# 		self.assertTrue(isinstance(colors, Color))
# 		self.assertTrue(isinstance(colors, str))
# 		self.assertEqual(colors, '\x1b[45;30m')
# 		self.assertEqual(colors.code, '45;30')
# 		self.assertEqual(repr(colors), '<Color: BG_Magenta|FG_Black>')
#
# 	def test_sub_subclass_with_new_new(self):
#
# 		class StrFlag(str, Flag):
#
# 			def __new__(cls, value, code):
# 				str_value = '\x1b[%sm' % code
# 				obj = str.__new__(cls, str_value)
# 				obj._value_ = value
# 				obj.code = code
# 				return obj
#
# 			@classmethod
# 			def _create_pseudo_member_(cls, value):
# 				pseudo_member = cls._value2member_map_.get(value, None)
# 				if pseudo_member is None:
# 					# calculate the code
# 					members, _ = _decompose(cls, value)
# 					code = ';'.join(m.code for m in members)
# 					pseudo_member = super(Color, cls)._create_pseudo_member_(value, code)
# 				return pseudo_member
#
# 			#
# 		class Color(StrFlag):
# 			_settings_ = AutoValue
# 			_order_ = 'FG_Black FG_Red FG_Green FG_Blue BG_Yellow BG_Magenta BG_Cyan BG_White'
#
# 			def __new__(cls, value, string, abbr):
# 				str_value = abbr.title()
# 				obj = str.__new__(cls, str_value)
# 				obj._value_ = value
# 				obj.code = string
# 				obj.abbr = abbr
# 				return obj
# 				# # FOREGROUND - 30s  BACKGROUND - 40s:
#
# 			FG_Black = '30', 'blk'  # ESC [ 30 m      # black
# 			FG_Red = '31', 'red'  # ESC [ 31 m      # red
# 			FG_Green = '32', 'grn'  # ESC [ 32 m      # green
# 			FG_Blue = '34', 'blu'  # ESC [ 34 m      # blue
# 			#
# 			BG_Yellow = '43', 'ylw'  # ESC [ 33 m      # yellow
# 			BG_Magenta = '45', 'mag'  # ESC [ 35 m      # magenta
# 			BG_Cyan = '46', 'cyn'  # ESC [ 36 m      # cyan
# 			BG_White = '47', 'wht'  # ESC [ 37 m      # white
#
# 			#
# 			def __repr__(self):
# 				if self._name_ is not None:
# 					return '<%s.%s>' % (self.__class__.__name__, self._name_)
# 				else:
# 					return '<%s: %s>' % (self.__class__.__name__, '|'.join([m.name for m in self]))
#
# 		self.assertTrue(isinstance(Color.FG_Black, Color))
# 		self.assertTrue(isinstance(Color.FG_Black, str))
# 		self.assertEqual(Color.FG_Black, 'Blk', str.__repr__(Color.FG_Black))
# 		self.assertEqual(Color.FG_Black.abbr, 'blk')
#
# 	def test_subclass_with_default_new(self):
#
# 		class MyFlag(str, Flag):
# 			_settings_ = AutoValue
# 			_order_ = 'this these theother'
# 			this = 'that'
# 			these = 'those'
# 			theother = 'thingimibobs'
#
# 		self.assertEqual(MyFlag.this, 'that')
# 		self.assertEqual(MyFlag.this.value, 1)
# 		self.assertEqual(MyFlag.these, 'those')
# 		self.assertEqual(MyFlag.these.value, 2)
# 		self.assertEqual(MyFlag.theother, 'thingimibobs')
# 		self.assertEqual(MyFlag.theother.value, 4)
#
# 	def test_extend_flag(self):
#
# 		class Color(Flag):
# 			BLACK = 0
# 			RED = 1
# 			GREEN = 2
# 			BLUE = 4
#
# 		extend_enum(Color, 'PURPLE', 5)
# 		self.assertTrue(Color(5) is Color.PURPLE)
# 		self.assertTrue(isinstance(Color.PURPLE, Color))
# 		self.assertEqual(Color.PURPLE.value, 5)
#
# 	def test_extend_flag_subclass(self):
#
# 		class Color(str, Flag):
# 			_order_ = 'FG_Black FG_Red FG_Green FG_Blue BG_Yellow BG_Magenta BG_Cyan BG_White'
# 			_settings_ = AutoValue
#
# 			def __new__(cls, value, code=None):
# 				str_value = '\x1b[%sm' % code
# 				obj = str.__new__(cls, str_value)
# 				obj._value_ = value
# 				obj.code = code
# 				return obj
#
# 			@staticmethod
# 			def _generate_next_value_(name, start, count, values, *args, **kwds):
# 				return (2**count, ) + args
#
# 			@classmethod
# 			def _create_pseudo_member_(cls, value):
# 				pseudo_member = cls._value2member_map_.get(value, None)
# 				if pseudo_member is None:
# 					# calculate the code
# 					members, _ = _decompose(cls, value)
# 					code = ';'.join(m.code for m in members)
# 					pseudo_member = super(Color, cls)._create_pseudo_member_(value, code)
# 				return pseudo_member
#
# 			#
# 			# # FOREGROUND - 30s  BACKGROUND - 40s:
# 			FG_Black = '30'  # ESC [ 30 m      # black
# 			FG_Red = '31'  # ESC [ 31 m      # red
# 			FG_Green = '32'  # ESC [ 32 m      # green
# 			FG_Blue = '34'  # ESC [ 34 m      # blue
# 			#
# 			BG_Yellow = '43'  # ESC [ 33 m      # yellow
# 			BG_Magenta = '45'  # ESC [ 35 m      # magenta
# 			BG_Cyan = '46'  # ESC [ 36 m      # cyan
# 			BG_White = '47'  # ESC [ 37 m      # white
#
# 			#
# 			def __repr__(self):
# 				if self._name_ is not None:
# 					return '<%s.%s>' % (self.__class__.__name__, self._name_)
# 				else:
# 					return '<%s: %s>' % (self.__class__.__name__, '|'.join([m.name for m in self]))
#
# 		#
# 		Purple = Color.BG_Magenta | Color.FG_Blue
# 		self.assertTrue(isinstance(Purple, Color))
# 		self.assertTrue(isinstance(Purple, str))
# 		self.assertIs(Purple, Color.BG_Magenta | Color.FG_Blue)
# 		self.assertEqual(Purple, '\x1b[45;34m')
# 		self.assertEqual(Purple.code, '45;34')
# 		self.assertIs(Purple.name, None)
#





class TestIntFlag(TestCase):
	"""Tests of the IntFlags."""

	class Perm(IntFlag):
		X = 1 << 0
		W = 1 << 1
		R = 1 << 2

	class Color(IntFlag):
		BLACK = 0
		RED = 1
		GREEN = 2
		BLUE = 4
		PURPLE = RED | BLUE

	class Open(IntFlag):
		"not a good flag candidate"
		RO = 0
		WO = 1
		RW = 2
		AC = 3
		CE = 1 << 19

	def test_membership(self):
		Color = self.Color
		Open = self.Open
		self.assertRaises(TypeError, lambda: 'GREEN' in Color)
		self.assertRaises(TypeError, lambda: 'RW' in Open)
		self.assertTrue(Color.GREEN in Color)
		self.assertTrue(Open.RW in Open)
		self.assertFalse(Color.GREEN in Open)
		self.assertFalse(Open.RW in Color)
		self.assertRaises(TypeError, lambda: 2 in Color)
		self.assertRaises(TypeError, lambda: 2 in Open)

	def test_member_contains(self):
		Color = self.Color
		self.assertRaises(TypeError, lambda: 'test' in Color.RED)
		self.assertRaises(TypeError, lambda: 1 in Color.RED)
		self.assertTrue(Color.RED in Color.RED)
		self.assertTrue(Color.RED in Color.PURPLE)

	def test_name_lookup(self):
		Color = self.Color
		self.assertTrue(Color.RED is Color['RED'])
		self.assertTrue(Color.RED | Color.GREEN is Color['RED|GREEN'])
		self.assertTrue(Color.PURPLE is Color['RED|BLUE'])

	def test_type(self):
		Perm = self.Perm
		Open = self.Open
		for f in Perm:
			self.assertTrue(isinstance(f, Perm))
			self.assertEqual(f, f.value)
		self.assertTrue(isinstance(Perm.W | Perm.X, Perm))
		self.assertEqual(Perm.W | Perm.X, 3)
		for f in Open:
			self.assertTrue(isinstance(f, Open))
			self.assertEqual(f, f.value)
		self.assertTrue(isinstance(Open.WO | Open.RW, Open))
		self.assertEqual(Open.WO | Open.RW, 3)

	def test_str(self):
		Perm = self.Perm
		self.assertEqual(str(Perm.R), 'Perm.R')
		self.assertEqual(str(Perm.W), 'Perm.W')
		self.assertEqual(str(Perm.X), 'Perm.X')
		self.assertEqual(str(Perm.R | Perm.W), 'Perm.R|W')
		self.assertEqual(str(Perm.R | Perm.W | Perm.X), 'Perm.R|W|X')
		self.assertEqual(str(Perm.R | 8), 'Perm.8|R')
		self.assertEqual(str(Perm(0)), 'Perm.0')
		self.assertEqual(str(Perm(8)), 'Perm.8')
		self.assertEqual(str(~Perm.R), 'Perm.W|X')
		self.assertEqual(str(~Perm.W), 'Perm.R|X')
		self.assertEqual(str(~Perm.X), 'Perm.R|W')
		self.assertEqual(str(~(Perm.R | Perm.W)), 'Perm.X')
		self.assertEqual(str(~(Perm.R | Perm.W | Perm.X)), 'Perm.-8')
		self.assertEqual(str(~(Perm.R | 8)), 'Perm.W|X')
		self.assertEqual(str(Perm(~0)), 'Perm.R|W|X')
		self.assertEqual(str(Perm(~8)), 'Perm.R|W|X')

		Open = self.Open
		self.assertEqual(str(Open.RO), 'Open.RO')
		self.assertEqual(str(Open.WO), 'Open.WO')
		self.assertEqual(str(Open.AC), 'Open.AC')
		self.assertEqual(str(Open.RO | Open.CE), 'Open.CE')
		self.assertEqual(str(Open.WO | Open.CE), 'Open.CE|WO')
		self.assertEqual(str(Open(4)), 'Open.4')
		self.assertEqual(str(~Open.RO), 'Open.CE|AC|RW|WO')
		self.assertEqual(str(~Open.WO), 'Open.CE|RW')
		self.assertEqual(str(~Open.AC), 'Open.CE')
		self.assertEqual(str(~(Open.RO | Open.CE)), 'Open.AC|RW|WO')
		self.assertEqual(str(~(Open.WO | Open.CE)), 'Open.RW')
		self.assertEqual(str(Open(~4)), 'Open.CE|AC|RW|WO')

	def test_repr(self):
		Perm = self.Perm
		self.assertEqual(repr(Perm.R), '<Perm.R: 4>')
		self.assertEqual(repr(Perm.W), '<Perm.W: 2>')
		self.assertEqual(repr(Perm.X), '<Perm.X: 1>')
		self.assertEqual(repr(Perm.R | Perm.W), '<Perm.R|W: 6>')
		self.assertEqual(repr(Perm.R | Perm.W | Perm.X), '<Perm.R|W|X: 7>')
		self.assertEqual(repr(Perm.R | 8), '<Perm.8|R: 12>')
		self.assertEqual(repr(Perm(0)), '<Perm.0: 0>')
		self.assertEqual(repr(Perm(8)), '<Perm.8: 8>')
		self.assertEqual(repr(~Perm.R), '<Perm.W|X: -5>')
		self.assertEqual(repr(~Perm.W), '<Perm.R|X: -3>')
		self.assertEqual(repr(~Perm.X), '<Perm.R|W: -2>')
		self.assertEqual(repr(~(Perm.R | Perm.W)), '<Perm.X: -7>')
		self.assertEqual(repr(~(Perm.R | Perm.W | Perm.X)), '<Perm.-8: -8>')
		self.assertEqual(repr(~(Perm.R | 8)), '<Perm.W|X: -13>')
		self.assertEqual(repr(Perm(~0)), '<Perm.R|W|X: -1>')
		self.assertEqual(repr(Perm(~8)), '<Perm.R|W|X: -9>')

		Open = self.Open
		self.assertEqual(repr(Open.RO), '<Open.RO: 0>')
		self.assertEqual(repr(Open.WO), '<Open.WO: 1>')
		self.assertEqual(repr(Open.AC), '<Open.AC: 3>')
		self.assertEqual(repr(Open.RO | Open.CE), '<Open.CE: 524288>')
		self.assertEqual(repr(Open.WO | Open.CE), '<Open.CE|WO: 524289>')
		self.assertEqual(repr(Open(4)), '<Open.4: 4>')
		self.assertEqual(repr(~Open.RO), '<Open.CE|AC|RW|WO: -1>')
		self.assertEqual(repr(~Open.WO), '<Open.CE|RW: -2>')
		self.assertEqual(repr(~Open.AC), '<Open.CE: -4>')
		self.assertEqual(repr(~(Open.RO | Open.CE)), '<Open.AC|RW|WO: -524289>')
		self.assertEqual(repr(~(Open.WO | Open.CE)), '<Open.RW: -524290>')
		self.assertEqual(repr(Open(~4)), '<Open.CE|AC|RW|WO: -5>')

	def test_or(self):
		Perm = self.Perm
		for i in Perm:
			for j in Perm:
				self.assertEqual(i | j, i.value | j.value)
				self.assertEqual((i | j).value, i.value | j.value)
				self.assertIs(type(i | j), Perm)
			for j in range(8):
				self.assertEqual(i | j, i.value | j)
				self.assertEqual((i | j).value, i.value | j)
				self.assertIs(type(i | j), Perm)
				self.assertEqual(j | i, j | i.value)
				self.assertEqual((j | i).value, j | i.value)
				self.assertIs(type(j | i), Perm)
		for i in Perm:
			self.assertIs(i | i, i)
			self.assertIs(i | 0, i)
			self.assertIs(0 | i, i)
		Open = self.Open
		self.assertIs(Open.RO | Open.CE, Open.CE)

	def test_and(self):
		Perm = self.Perm
		RW = Perm.R | Perm.W
		RX = Perm.R | Perm.X
		WX = Perm.W | Perm.X
		RWX = Perm.R | Perm.W | Perm.X
		values = list(Perm) + [RW, RX, WX, RWX, Perm(0)]
		for i in values:
			for j in values:
				self.assertEqual(i & j, i.value & j.value, 'i is %r, j is %r' % (i, j))
				self.assertEqual((i & j).value, i.value & j.value, 'i is %r, j is %r' % (i, j))
				self.assertIs(type(i & j), Perm, 'i is %r, j is %r' % (i, j))
			for j in range(8):
				self.assertEqual(i & j, i.value & j)
				self.assertEqual((i & j).value, i.value & j)
				self.assertIs(type(i & j), Perm)
				self.assertEqual(j & i, j & i.value)
				self.assertEqual((j & i).value, j & i.value)
				self.assertIs(type(j & i), Perm)
		for i in Perm:
			self.assertIs(i & i, i)
			self.assertIs(i & 7, i)
			self.assertIs(7 & i, i)
		Open = self.Open
		self.assertIs(Open.RO & Open.CE, Open.RO)

	def test_xor(self):
		Perm = self.Perm
		for i in Perm:
			for j in Perm:
				self.assertEqual(i ^ j, i.value ^ j.value)
				self.assertEqual((i ^ j).value, i.value ^ j.value)
				self.assertIs(type(i ^ j), Perm)
			for j in range(8):
				self.assertEqual(i ^ j, i.value ^ j)
				self.assertEqual((i ^ j).value, i.value ^ j)
				self.assertIs(type(i ^ j), Perm)
				self.assertEqual(j ^ i, j ^ i.value)
				self.assertEqual((j ^ i).value, j ^ i.value)
				self.assertIs(type(j ^ i), Perm)
		for i in Perm:
			self.assertIs(i ^ 0, i)
			self.assertIs(0 ^ i, i)
		Open = self.Open
		self.assertIs(Open.RO ^ Open.CE, Open.CE)
		self.assertIs(Open.CE ^ Open.CE, Open.RO)

	def test_invert(self):
		Perm = self.Perm
		RW = Perm.R | Perm.W
		RX = Perm.R | Perm.X
		WX = Perm.W | Perm.X
		RWX = Perm.R | Perm.W | Perm.X
		values = list(Perm) + [RW, RX, WX, RWX, Perm(0)]
		for i in values:
			self.assertEqual(~i, ~i.value)
			self.assertEqual((~i).value, ~i.value)
			self.assertIs(type(~i), Perm)
			self.assertEqual(~~i, i)
		for i in Perm:
			self.assertIs(~~i, i)
		Open = self.Open
		self.assertIs(Open.WO & ~Open.WO, Open.RO)
		self.assertIs((Open.WO | Open.CE) & ~Open.WO, Open.CE)

	def test_iter(self):
		Perm = self.Perm
		NoPerm = Perm.R ^ Perm.R
		RWX = Perm.R | Perm.W | Perm.X
		self.assertEqual(list(NoPerm), [])
		self.assertEqual(list(Perm.R), [Perm.R])
		self.assertEqual(list(RWX), [Perm.R, Perm.W, Perm.X])

	def test_programatic_function_string(self):
		Perm = IntFlag('Perm', 'R W X')
		lst = list(Perm)
		self.assertEqual(len(lst), len(Perm))
		self.assertEqual(len(Perm), 3, Perm)
		self.assertEqual(lst, [Perm.R, Perm.W, Perm.X])
		for i, n in enumerate('R W X'.split()):
			v = 1 << i
			e = Perm(v)
			self.assertEqual(e.value, v)
			self.assertEqual(type(e.value), int)
			self.assertEqual(e, v)
			self.assertEqual(e.name, n)
			self.assertIn(e, Perm)
			self.assertIs(type(e), Perm)

	def test_programatic_function_string_with_start(self):
		Perm = IntFlag('Perm', 'R W X', start=8)
		lst = list(Perm)
		self.assertEqual(len(lst), len(Perm))
		self.assertEqual(len(Perm), 3, Perm)
		self.assertEqual(lst, [Perm.R, Perm.W, Perm.X])
		for i, n in enumerate('R W X'.split()):
			v = 8 << i
			e = Perm(v)
			self.assertEqual(e.value, v)
			self.assertEqual(type(e.value), int)
			self.assertEqual(e, v)
			self.assertEqual(e.name, n)
			self.assertIn(e, Perm)
			self.assertIs(type(e), Perm)

	def test_programatic_function_string_list(self):
		Perm = IntFlag('Perm', ['R', 'W', 'X'])
		lst = list(Perm)
		self.assertEqual(len(lst), len(Perm))
		self.assertEqual(len(Perm), 3, Perm)
		self.assertEqual(lst, [Perm.R, Perm.W, Perm.X])
		for i, n in enumerate('R W X'.split()):
			v = 1 << i
			e = Perm(v)
			self.assertEqual(e.value, v)
			self.assertEqual(type(e.value), int)
			self.assertEqual(e, v)
			self.assertEqual(e.name, n)
			self.assertIn(e, Perm)
			self.assertIs(type(e), Perm)

	def test_programatic_function_iterable(self):
		Perm = IntFlag('Perm', (('R', 2), ('W', 8), ('X', 32)))
		lst = list(Perm)
		self.assertEqual(len(lst), len(Perm))
		self.assertEqual(len(Perm), 3, Perm)
		self.assertEqual(lst, [Perm.R, Perm.W, Perm.X])
		for i, n in enumerate('R W X'.split()):
			v = 1 << (2 * i + 1)
			e = Perm(v)
			self.assertEqual(e.value, v)
			self.assertEqual(type(e.value), int)
			self.assertEqual(e, v)
			self.assertEqual(e.name, n)
			self.assertIn(e, Perm)
			self.assertIs(type(e), Perm)

	def test_programatic_function_from_dict(self):
		Perm = IntFlag('Perm', OrderedDict((('R', 2), ('W', 8), ('X', 32))))
		lst = list(Perm)
		self.assertEqual(len(lst), len(Perm))
		self.assertEqual(len(Perm), 3, Perm)
		self.assertEqual(lst, [Perm.R, Perm.W, Perm.X])
		for i, n in enumerate('R W X'.split()):
			v = 1 << (2 * i + 1)
			e = Perm(v)
			self.assertEqual(e.value, v)
			self.assertEqual(type(e.value), int)
			self.assertEqual(e, v)
			self.assertEqual(e.name, n)
			self.assertIn(e, Perm)
			self.assertIs(type(e), Perm)

	def test_containment(self):
		Perm = self.Perm
		R, W, X = Perm
		RW = R | W
		RX = R | X
		WX = W | X
		RWX = R | W | X
		self.assertTrue(R in RW)
		self.assertTrue(R in RX)
		self.assertTrue(R in RWX)
		self.assertTrue(W in RW)
		self.assertTrue(W in WX)
		self.assertTrue(W in RWX)
		self.assertTrue(X in RX)
		self.assertTrue(X in WX)
		self.assertTrue(X in RWX)
		self.assertFalse(R in WX)
		self.assertFalse(W in RX)
		self.assertFalse(X in RW)

	def test_bool(self):
		Perm = self.Perm
		for f in Perm:
			self.assertTrue(f)
		Open = self.Open
		for f in Open:
			self.assertEqual(bool(f.value), bool(f))

	@unittest.skipUnless(threading, 'Threading required for this test.')
	def test_unique_composite(self):
		# override __eq__ to be identity only
		class TestFlag(IntFlag):
			_order_ = 'one two three four five six seven eight'
			one = auto()
			two = auto()
			three = auto()
			four = auto()
			five = auto()
			six = auto()
			seven = auto()
			eight = auto()

			def __eq__(self, other):
				return self is other

			def __hash__(self):
				return hash(self._value_)

		# have multiple threads competing to complete the composite members
		seen = set()
		failed = [False]

		def cycle_enum():
			# nonlocal failed
			try:
				for i in range(256):
					seen.add(TestFlag(i))
			except Exception:
				failed[0] = True

		threads = [threading.Thread(target=cycle_enum) for _ in range(8)]
		for t in threads:
			t.start()
		for t in threads:
			t.join()
		# check that only 248 members were created (8 were created originally)
		self.assertFalse(failed[0], 'at least one thread failed while creating composite members')
		self.assertEqual(256, len(seen), 'too many composite members created')

