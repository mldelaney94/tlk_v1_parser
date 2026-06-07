from __future__ import annotations

from dataclasses import dataclass, field, InitVar
import struct


@dataclass
class Header:
  """Class for storing header information."""
  b_version: bytes
  b_misc1: bytes
  b_num_of_strings: bytes
  b_string_start: bytes
  i_start_of_strings: int = field(init=False)
  i_num_of_strings: int = field(init=False)

  def __post_init__(self) -> None:
    self.i_start_of_strings = int.from_bytes(
      self.b_string_start, byteorder='little')
    self.i_num_of_strings = int.from_bytes(
      self.b_num_of_strings, byteorder='little')

  def to_bytes(self) -> bytes:
    return (
      self.b_version + self.b_misc1 + self.b_num_of_strings +
      self.b_string_start
    )


@dataclass
class StringRef:
  b_flag: bytes
  b_sound_res_ref: bytes
  b_off_set: bytes
  b_str_len: bytes
  i_position: int = field(init=False)
  i_str_len: int = field(init=False)

  def __post_init__(self) -> None:
    self.i_position = int.from_bytes(self.b_off_set, byteorder='little')
    self.i_str_len = int.from_bytes(self.b_str_len, byteorder='little')

  def set_offset_and_length(self, offset: int, length: int) -> None:
    self.i_position = offset
    self.i_str_len = length
    self.b_off_set = struct.pack('<I', offset)
    self.b_str_len = struct.pack('<I', length)

  def copy(self) -> StringRef:
    return StringRef(
      self.b_flag,
      self.b_sound_res_ref,
      self.b_off_set,
      self.b_str_len,
    )

  def to_bytes(self) -> bytes:
    return self.b_flag + self.b_sound_res_ref + self.b_off_set + self.b_str_len


@dataclass
class StringRep:
  encoding: str
  str_string: str = field(init=False)
  b_string: InitVar[bytes]

  def __post_init__(self, b_string: bytes) -> None:
    self.str_string = b_string.decode(self.encoding)

  def copy(self) -> StringRep:
    return StringRep(self.encoding, self.str_string.encode(self.encoding))

  def to_bytes(self) -> bytes:
    return self.str_string.encode(self.encoding)
