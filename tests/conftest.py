from __future__ import annotations

import struct
from pathlib import Path

import pytest

from tlk_parser import Tlk


def write_minimal_tlk(path: Path, strings: list[str], encoding: str = 'utf_8') -> None:
  encoded = [s.encode(encoding) for s in strings]
  offsets: list[tuple[int, int]] = []
  offset = 0

  for data in encoded:
    if len(data) == 0:
      offsets.append((0, 0))
    else:
      offsets.append((offset, len(data)))
      offset += len(data)

  start = 18 + len(strings) * 26

  with path.open('wb') as f:
    f.write(b'TLK V1  ')
    f.write(b'\x00\x00')
    f.write(struct.pack('<I', len(strings)))
    f.write(struct.pack('<I', start))

    for off, length in offsets:
      f.write(struct.pack('<H', 1))
      f.write(b'\x00' * 16)
      f.write(struct.pack('<I', off))
      f.write(struct.pack('<I', length))

    for data in encoded:
      f.write(data)


@pytest.fixture
def minimal_tlk_path(tmp_path: Path) -> Path:
  path = tmp_path / 'minimal.tlk'
  write_minimal_tlk(path, ['<NO TEXT>', 'hello', '', 'world'])
  return path


@pytest.fixture
def minimal_tlk(minimal_tlk_path: Path) -> Tlk:
  return Tlk(minimal_tlk_path)
