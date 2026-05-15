#!/usr/bin/env python3
"""
Bitfield Decode - Extract bitfield values from a hex or decimal number.

Usage:
    bitfield_decode.py [-l|--list] [value] [bitfields]
    
    -l, --list: Output each bitfield on a separate line with alignment
    value: Hex (0x###) or decimal number
    bitfields: Space or comma-separated bitfield specs (e.g., "31:26 25:20 19")
    
    If no arguments provided, enters interactive mode.
"""

import sys
import re
import argparse

# Try to import readline for command history (optional)
try:
    import readline  # Unix/Linux/macOS
except ImportError:
    try:
        import pyreadline3 as readline  # Windows
    except ImportError:
        readline = None  # No readline available


def parse_value(value_str):
    """Parse a value string as hex or decimal."""
    value_str = value_str.strip()
    try:
        if value_str.lower().startswith('0x'):
            return int(value_str, 16)
        else:
            return int(value_str)
    except ValueError:
        raise ValueError(f"Invalid value: {value_str}")


def parse_bitfields(bitfields_str):
    """Parse bitfield specification string into list of (high, low) tuples."""
    # Replace commas with spaces and normalize whitespace
    bitfields_str = bitfields_str.replace(',', ' ')
    # Split by whitespace and filter empty strings
    parts = [p for p in bitfields_str.split() if p]
    
    bitfields = []
    for part in parts:
        part = part.strip()
        if ':' in part:
            # Range notation (high:low)
            try:
                high, low = part.split(':')
                high = int(high)
                low = int(low)
                if high < low:
                    raise ValueError(f"Invalid range {part}: high bit must be >= low bit")
                bitfields.append((high, low))
            except (ValueError, IndexError) as e:
                raise ValueError(f"Invalid bitfield specification: {part}")
        else:
            # Single bit
            try:
                bit = int(part)
                if bit < 0:
                    raise ValueError(f"Invalid bit position: {bit}")
                bitfields.append((bit, bit))
            except ValueError:
                raise ValueError(f"Invalid bitfield specification: {part}")
    
    return bitfields


def extract_bitfield(value, high, low):
    """Extract bitfield value from the given range."""
    # Create mask for the bitfield width
    width = high - low + 1
    mask = (1 << width) - 1
    # Shift and mask to extract the field
    return (value >> low) & mask


def decode_bitfields(value, bitfields):
    """Extract all bitfield values from the given value."""
    results = []
    for high, low in bitfields:
        field_value = extract_bitfield(value, high, low)
        results.append(field_value)
    return results


def format_output(values):
    """Format extracted values as hex strings."""
    return ' '.join(f"x{v:X}" for v in values)


def format_verbose_output(bitfields, values):
    """Format output with each bitfield on a separate line."""
    lines = []
    
    # Find the maximum length of the bitfield spec for alignment
    max_len = 0
    bitfield_specs = []
    for high, low in bitfields:
        if high == low:
            spec = str(high)
        else:
            spec = f"{high}:{low}"
        bitfield_specs.append(spec)
        max_len = max(max_len, len(spec))
    
    # Format each line
    for spec, (high, low), value in zip(bitfield_specs, bitfields, values):
        # For single bits, output just 1 or 0
        if high == low:
            value_str = str(value)
        else:
            value_str = f"x{value:X}"
        
        # Right-align the spec and add colon with spaces
        aligned_spec = spec.rjust(max_len)
        lines.append(f"{aligned_spec} : {value_str}")
    
    return '\n'.join(lines)


def process_line(line, list_mode=False):
    """Process a single line of input."""
    parts = line.strip().split(None, 1)
    if len(parts) < 2:
        return None, "Error: Need both value and bitfields"
    
    value_str, bitfields_str = parts
    
    try:
        value = parse_value(value_str)
        bitfields = parse_bitfields(bitfields_str)
        if not bitfields:
            return None, "Error: No valid bitfields specified"
        results = decode_bitfields(value, bitfields)
        if list_mode:
            return format_verbose_output(bitfields, results), None
        else:
            return format_output(results), None
    except ValueError as e:
        return None, f"Error: {e}"


def interactive_mode(list_mode=False):
    """Run in interactive mode."""
    print("Bitfield Decoder - Interactive Mode")
    print("Enter value and bitfields (e.g., '0x1234 15:12 11:8 7:0')")
    print("Type 'quit' or 'exit' to end, or press Ctrl+C")
    print()
    
    while True:
        try:
            line = input("> ").strip()
            if line.lower() in ('quit', 'exit', 'q'):
                break
            if not line:
                continue
                
            result, error = process_line(line, list_mode)
            if error:
                print(error)
            else:
                print(result)
                
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except EOFError:
            break


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Extract bitfield values from a hex or decimal number.',
        add_help=False
    )
    parser.add_argument('-l', '--list', action='store_true',
                        help='Output each bitfield on a separate line with alignment')
    parser.add_argument('-h', '--help', action='store_true',
                        help='Show this help message')
    parser.add_argument('value', nargs='?',
                        help='Hex (0x###) or decimal number')
    parser.add_argument('bitfields', nargs='?',
                        help='Space or comma-separated bitfield specs')
    
    args = parser.parse_args()
    
    if args.help:
        print("Usage: bitfield_decode.py [-l|--list] [value] [bitfields]", file=sys.stderr)
        print("  -l, --list: Output each bitfield on a separate line", file=sys.stderr)
        print("  value: Hex (0x###) or decimal number", file=sys.stderr)
        print("  bitfields: Space or comma-separated bitfield specs", file=sys.stderr)
        print("  Example: bitfield_decode.py 0x5453 '15:12 11:7 6:5 4:0'", file=sys.stderr)
        print("  Or run without arguments for interactive mode", file=sys.stderr)
        sys.exit(0)
    
    if args.value is None and args.bitfields is None:
        # No arguments - interactive mode
        interactive_mode(args.list)
    elif args.value is not None and args.bitfields is not None:
        # Command-line mode
        try:
            value = parse_value(args.value)
            bitfields = parse_bitfields(args.bitfields)
            if not bitfields:
                print("Error: No valid bitfields specified", file=sys.stderr)
                sys.exit(1)
            results = decode_bitfields(value, bitfields)
            if args.list:
                print(format_verbose_output(bitfields, results))
            else:
                print(format_output(results))
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print("Usage: bitfield_decode.py [-l|--list] [value] [bitfields]", file=sys.stderr)
        print("  value: Hex (0x###) or decimal number", file=sys.stderr)
        print("  bitfields: Space or comma-separated bitfield specs", file=sys.stderr)
        print("  Example: bitfield_decode.py 0x5453 '15:12 11:7 6:5 4:0'", file=sys.stderr)
        print("  Or run without arguments for interactive mode", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()