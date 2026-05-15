# Bitfield Tools

A collection of Python utilities for working with hardware register bitfields.

- `bitfield_decode.py` - Bitfield Decoder
- `register_decode.py` - Register Dump Decoder

## `bitfield_decode.py` - Bitfield Value Extractor

Extract bitfield values from a single hex or decimal number.

**Usage:**
```bash
python bitfield_decode.py [-l|--list] [value] [bitfields]
```

**Arguments:**
- `-l, --list`: Output each bitfield on a separate line with alignment
- `value`: Hex (0x###) or decimal number
- `bitfields`: Space or comma-separated bitfield specs

**Examples:**
```bash
# Extract specific bitfields from a hex value
python bitfield_decode.py 0x5453 "15:12 11:7 6:5 4:0"
# Output: x5 x8 x2 x13

# Extract bitfields from decimal input
python bitfield_decode.py 21587 "15:12 11:7 6:5 4:0"
# Output: x5 x8 x2 x13

# Using comma-separated values for bitfields
python bitfield_decode.py 21587 "15:12,11:7,6:5,4:0"
# Output: x5 x8 x2 x13

# Use list mode for verbose output
python bitfield_decode.py --list 0x5453 "15:12 11:7 6:5 4 3:0"
# Output:
# 15:12 : x5
#  11:7 : x8
#   6:5 : x2
#     4 : 1
#   3:0 : x3

# Single bits output as 0 or 1 in list mode
python bitfield_decode.py -l 0xD "3 2 1 0"
# Output:
# 3 : 1
# 2 : 1
# 1 : 0
# 0 : 1

# Interactive mode (run without arguments)
python bitfield_decode.py
# > 0xFF 7:4 3:0
# xF xF
# > 0x5453 15:12 11:7 6:5 4 3:0
# x5 x8 x2 x1 x3
```

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

## License

MIT License - see LICENSE file for details
