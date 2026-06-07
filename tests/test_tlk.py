from pathlib import Path

import pytest

from tlk_parser import Tlk


def test_loads_header_and_strings(minimal_tlk: Tlk) -> None:
  assert minimal_tlk.header.i_num_of_strings == 4
  assert minimal_tlk.string_reps[0].str_string == '<NO TEXT>'
  assert minimal_tlk.string_reps[1].str_string == 'hello'
  assert minimal_tlk.string_reps[2].str_string == ''
  assert minimal_tlk.string_reps[3].str_string == 'world'


def test_empty_string_refs_have_zero_offset_and_length(minimal_tlk: Tlk) -> None:
  assert minimal_tlk.string_refs[2].i_position == 0
  assert minimal_tlk.string_refs[2].i_str_len == 0


def test_map_strings_returns_new_instance(minimal_tlk: Tlk) -> None:
  mapped = minimal_tlk.map_strings(str.upper)
  assert mapped is not minimal_tlk


def test_map_strings_does_not_mutate_original(minimal_tlk: Tlk) -> None:
  original = [rep.str_string for rep in minimal_tlk.string_reps]
  minimal_tlk.map_strings(str.upper)
  assert [rep.str_string for rep in minimal_tlk.string_reps] == original


def test_map_strings_applies_function(minimal_tlk: Tlk) -> None:
  mapped = minimal_tlk.map_strings(str.upper)
  assert mapped.string_reps[0].str_string == '<NO TEXT>'
  assert mapped.string_reps[1].str_string == 'HELLO'
  assert mapped.string_reps[3].str_string == 'WORLD'


def test_map_strings_recalculates_offsets_when_lengths_change(minimal_tlk: Tlk) -> None:
  mapped = minimal_tlk.map_strings(lambda s: s + '!' if s else s)

  first_len = len('<NO TEXT>!'.encode('utf_8'))
  second_len = len('hello!'.encode('utf_8'))
  third_len = len('world!'.encode('utf_8'))

  assert mapped.string_refs[1].i_position == first_len
  assert mapped.string_refs[1].i_str_len == second_len
  assert mapped.string_refs[3].i_position == first_len + second_len
  assert mapped.string_refs[3].i_str_len == third_len


def test_identity_map_roundtrip_is_byte_identical(minimal_tlk_path: Path) -> None:
  original_bytes = minimal_tlk_path.read_bytes()
  mapped = Tlk(minimal_tlk_path).map_strings(lambda s: s)
  out_path = minimal_tlk_path.parent / 'roundtrip.tlk'
  mapped.save_tlk(out_path)
  assert out_path.read_bytes() == original_bytes


def test_save_tlk_adds_extension(tmp_path: Path, minimal_tlk: Tlk) -> None:
  out_path = minimal_tlk.save_tlk(tmp_path / 'output')
  assert out_path == tmp_path / 'output.tlk'
  assert out_path.exists()


def test_save_tlk_keeps_explicit_extension(tmp_path: Path, minimal_tlk: Tlk) -> None:
  out_path = minimal_tlk.save_tlk(tmp_path / 'output.tlk')
  assert out_path == tmp_path / 'output.tlk'


def test_saved_file_can_be_reloaded(tmp_path: Path, minimal_tlk: Tlk) -> None:
  out_path = minimal_tlk.map_strings(lambda s: s.upper()).save_tlk(tmp_path / 'saved')
  reloaded = Tlk(out_path)
  assert [rep.str_string for rep in reloaded.string_reps] == [
    '<NO TEXT>', 'HELLO', '', 'WORLD'
  ]


@pytest.mark.skipif(
  not Path('dialog_zh.tlk').exists(),
  reason='dialog_zh.tlk not present',
)
def test_dialog_zh_loads() -> None:
  tlk = Tlk('dialog_zh.tlk')
  assert tlk.header.i_num_of_strings == len(tlk.string_refs) == len(tlk.string_reps)
  assert tlk.string_reps[0].str_string == '<NO TEXT>'
  assert tlk.string_reps[1].str_string


@pytest.mark.skipif(
  not Path('dialog_zh.tlk').exists(),
  reason='dialog_zh.tlk not present',
)
def test_dialog_zh_identity_roundtrip(tmp_path: Path) -> None:
  original_bytes = Path('dialog_zh.tlk').read_bytes()
  mapped = Tlk('dialog_zh.tlk').map_strings(lambda s: s)
  out_path = mapped.save_tlk(tmp_path / 'dialog_zh_copy')
  assert out_path.read_bytes() == original_bytes
