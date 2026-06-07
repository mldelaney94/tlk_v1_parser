from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import BinaryIO, Self

from tlk_parser.data_classes import Header, StringRef, StringRep


class Tlk:
  encoding: str
  source_path: Path
  header: Header
  string_refs: list[StringRef]
  string_reps: list[StringRep]

  def __init__(self, path: str | Path, encoding: str = 'utf_8') -> None:
    path = Path(path)
    self.encoding = encoding
    self.source_path = path

    with path.open('rb') as f:
      self.header = self._read_header(f)
      self.string_refs = [
        self._read_stringref(f)
        for _ in range(self.header.i_num_of_strings)
      ]
      self.string_reps = [
        self._read_stringrep(f, ref.i_str_len, encoding)
        for ref in self.string_refs
      ]

  def map_strings(self, fn: Callable[[str], str]) -> Self:
    copy = self._deep_copy()
    for rep in copy.string_reps:
      rep.str_string = fn(rep.str_string)
    copy._recalculate_offsets()
    return copy

  def save_tlk(self, basename: str | Path) -> Path:
    basename = Path(basename)
    if basename.suffix.lower() != '.tlk':
      output_path = basename.with_suffix('.tlk')
    else:
      output_path = basename

    with output_path.open('wb') as f:
      f.write(self.header.to_bytes())
      for ref in self.string_refs:
        f.write(ref.to_bytes())
      for rep in self.string_reps:
        f.write(rep.to_bytes())

    return output_path

  def _deep_copy(self) -> Tlk:
    tlk = Tlk.__new__(Tlk)
    tlk.encoding = self.encoding
    tlk.source_path = self.source_path
    tlk.header = self.header
    tlk.string_refs = [ref.copy() for ref in self.string_refs]
    tlk.string_reps = [rep.copy() for rep in self.string_reps]
    return tlk

  def _recalculate_offsets(self) -> None:
    offset = 0
    for ref, rep in zip(self.string_refs, self.string_reps, strict=True):
      length = len(rep.str_string.encode(self.encoding))
      if length == 0:
        ref.set_offset_and_length(0, 0)
      else:
        ref.set_offset_and_length(offset, length)
        offset += length

  @staticmethod
  def _read_header(f: BinaryIO) -> Header:
    return Header(
      f.read(8),
      f.read(2),
      f.read(4),
      f.read(4),
    )

  @staticmethod
  def _read_stringref(f: BinaryIO) -> StringRef:
    return StringRef(
      f.read(2),
      f.read(16),
      f.read(4),
      f.read(4),
    )

  @staticmethod
  def _read_stringrep(f: BinaryIO, str_len: int, encoding: str) -> StringRep:
    return StringRep(encoding, f.read(str_len))
