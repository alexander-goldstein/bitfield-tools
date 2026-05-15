# Bitfield Decoder

A Python tool for decoding hardware register values based on bitfield mappings. This utility helps analyze register dumps by extracting individual bitfield values and mapping them to human-readable descriptions.

## Features

- Extract individual bitfield values from register dumps
- Support for single-bit and multi-bit fields
- Decode values using configurable mapping tables
- Format output with proper hex notation and bit grouping
- Handle multi-line decode descriptions from CSV mappings

## Requirements & Installation

- Python 3.6 or higher
- No external dependencies (uses only Python standard library)

Clone this repository and run the scripts.

## Usage

```bash
python register_decode.py -m <mapping.csv> -i <reg_dump.csv> [-o <output.csv>] [-w <bits>]
```

### Arguments

- `-m, --map`: Register mapping CSV file (required)
- `-i, --inputs`: Input register dump CSV file (required)
- `-o, --output`: Output CSV file path (optional, defaults to `<input>_decoded.csv`)
- `-w, --width`: Default register width in bits (optional, default: 32)

### Examples

```bash
# Use default output filename (reg_dump_decoded.csv)
python register_decode.py -m mapping.csv -i reg_dump.csv

# Specify output filename and custom width
python register_decode.py -m mapping.csv -i reg_dump.csv -o decoded.csv -w 16

# Using long-form arguments
python register_decode.py --map mapping.csv --inputs reg_dump.csv --output decoded.csv --width 32
```

## Input File Formats

### Register Dump (`reg_dump.csv`)

Contains the register addresses and their current values:

```csv
Register, Value
0x5F,0x550D
0x62,0x101B000C
```

### Register Mapping (`mapping.csv`)

Defines the bitfield structure for each register. 

Newlines are supported by enclosing in quotes.

```csv
Address,Register Name,Register Width,Bitfield Range,Bitfield Name,Bitfield Description,Bitfield Decode
0x5F,M1_SW_MODE,,14,virtual_Step_enc,Source for virtual stop,"0x0: Ramp-generator position
0x1: Encoder position"
0x5F,M1_SW_MODE,,13,en_virtual_stop_r,Enable automatic stop,
0x5F,M1_SW_MODE,,12:10,multi_bit_field,A multi-bit field,"0x0: Option A
0x1: Option B"
```

**Column Details:**

- **Address**: Register address in hex (e.g., `0x5F`)
- **Register Name**: Human-readable register name
- **Register Width**: Width in bits (optional, uses default-width if empty)
- **Bitfield Range**: Bit position(s)
  - Single bit: `14`
  - Range: `23:16` (high:low notation)
- **Bitfield Name**: Name of the bitfield
- **Bitfield Description**: Detailed description (optional)
- **Bitfield Decode**: Value-to-meaning mappings (optional)
  - Format: `0xN: Description` (one per line within the cell)

## Output Format

The output CSV contains one row per bitfield:

```csv
Register,Register Name,Value (Bitfield Values),Bitfield,Bitfield Value,Decoding
0x5F,M1_SW_MODE,"0x550D (101,0101,0000,1101)",virtual_Step_enc[14],1,0x1: Encoder position
0x5F,M1_SW_MODE,"0x550D (101,0101,0000,1101)",en_virtual_stop_r[13],0,
```

## License

MIT License - see LICENSE file for details.