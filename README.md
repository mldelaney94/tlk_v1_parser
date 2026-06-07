# tlk-parser

Python library for reading, transforming, and writing BioWare **TLK V1** dialogue files (used in games such as *Baldurs Gate 2*).

## Install

```bash
pip install tlk-parser
```

For local development:

```bash
git clone https://github.com/mldelaney94/tlk_v1_parser.git
cd tlk_v1_parser
./setup_venv.sh
source ./activate_venv.sh
```

## Usage

```python
from tlk_parser import Tlk

tlk = Tlk("dialog.tlk")

# Inspect strings
for rep in tlk.string_reps:
    print(rep.str_string)

# Transform strings without mutating the original
translated = tlk.map_strings(lambda s: s.upper())
translated.save_tlk("dialog_upper.tlk")
```