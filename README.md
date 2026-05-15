# Bitfield Tools

A collection of Python utilities for working with hardware register bitfields.

- `register_decode.py` - Register Dump Decoder
- `bitfield_decode.py` - Bitfield Decoder

## `register_decode.py` - Register Dump Decoder

Decode register dumps using bitfield mapping files. Extracts individual bitfield values and maps them to human-readable descriptions.

**Example:**
```bash
# Use default output (input_decoded.csv) and 32-bit width
python register_decode.py --map data/mapping.csv --input data/reg_dump.csv

# Specify output and default bitfield width
python register_decode.py --map data/mapping.csv --input data/reg_dump.csv --output decoded.csv --width 16
```

**Arguments:**
- `-m, --map`: Register mapping CSV file (required)
- `-i, --inputs`: Input register dump CSV file (required)
- `-o, --output`: Output CSV file (optional, defaults to `<input>_decoded.csv`)
- `-w, --width`: Default register width in bits (optional, default: 32)

See the `data/` directory for example input and output files:
- `reg_dump.csv` - Sample register dump
- `mapping.csv` - Sample bitfield mappings
- `out.csv` - Expected decoder output

## 2. `bitfield_decode.py` - Bitfield Value Extractor

Extract bitfield values from a single hex or decimal number.

**Usage:**
```bash
python bitfield_decode.py [value] [bitfields]
```

**Examples:**
```bash
# Extract specific bitfields from a hex value
python bitfield_decode.py 0x5453 "15:12 11:7 6:5 4:0"
# Output: 0x5 0x8 0x2 0x13

# Use decimal input and comma separators
python bitfield_decode.py 21587 "15:12, 11:7, 6:5, 4:0"

# Interactive mode (run without arguments)
python bitfield_decode.py
> 0xFF 7:4 3:0
0xF 0xF
```

**Bitfield Format:**
- Single bit: `15` or `8`
- Range: `31:26` (high:low)
- Separators: spaces, commas, or both

## Requirements

Python 3.6+ (no external dependencies)

## License

MIT License - see LICENSE file for details
