#!/usr/bin/env python3
"""
Bitfield Decode - Extract bitfield values from a hex or decimal number.

Usage:
    bitfield_decode.py [value] [bitfields]
    
    value: Hex (0x###) or decimal number
    bitfields: Space or comma-separated bitfield specs (e.g., "31:26 25:20 19")
    
    If no arguments provided, enters interactive mode.
"""

import sys
import re


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
    return ' '.join(f"0x{v:X}" for v in values)


def process_line(line):
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
        return format_output(results), None
    except ValueError as e:
        return None, f"Error: {e}"


def interactive_mode():
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
                
            result, error = process_line(line)
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
    if len(sys.argv) == 1:
        # No arguments - interactive mode
        interactive_mode()
    elif len(sys.argv) == 3:
        # Command-line mode
        value_str = sys.argv[1]
        bitfields_str = sys.argv[2]
        
        try:
            value = parse_value(value_str)
            bitfields = parse_bitfields(bitfields_str)
            if not bitfields:
                print("Error: No valid bitfields specified", file=sys.stderr)
                sys.exit(1)
            results = decode_bitfields(value, bitfields)
            print(format_output(results))
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print("Usage: bitfield_decode.py [value] [bitfields]", file=sys.stderr)
        print("  value: Hex (0x###) or decimal number", file=sys.stderr)
        print("  bitfields: Space or comma-separated bitfield specs", file=sys.stderr)
        print("  Example: bitfield_decode.py 0x5453 '15:12 11:7 6:5 4:0'", file=sys.stderr)
        print("  Or run without arguments for interactive mode", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()