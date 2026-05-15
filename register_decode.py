#!/usr/bin/env python3
"""
Bitfield Decoder - A tool to decode register values based on bitfield mappings.
"""

import argparse
import csv
import sys
from typing import Dict, List, Tuple, Optional


class BitfieldMapping:
    """Represents a single bitfield mapping."""
    
    def __init__(self, address: str, register_name: str, register_width: Optional[int], 
                 bitfield_range: str, bitfield_name: str, bitfield_description: str, 
                 bitfield_decode: str):
        self.address = address
        self.register_name = register_name
        self.register_width = register_width
        self.bitfield_range = bitfield_range
        self.bitfield_name = bitfield_name
        self.bitfield_description = bitfield_description
        self.bitfield_decode = bitfield_decode
        self.bit_positions = self._parse_bitfield_range(bitfield_range)
    
    def _parse_bitfield_range(self, range_str: str) -> List[int]:
        """Parse bitfield range string and return list of bit positions."""
        if not range_str or not range_str.strip():
            return []
            
        range_str = range_str.strip()
        
        if ':' in range_str:
            # Range notation (high:low)
            parts = range_str.split(':')
            high = int(parts[0])
            low = int(parts[1])
            return list(range(low, high + 1))
        elif range_str.startswith('{'):
            # Width notation {n} - handled by the reader
            return []
        else:
            # Single bit
            return [int(range_str)]
    
    def extract_value(self, register_value: int) -> int:
        """Extract the bitfield value from the register value."""
        if not self.bit_positions:
            return 0
        
        value = 0
        for i, bit_pos in enumerate(sorted(self.bit_positions)):
            if register_value & (1 << bit_pos):
                value |= (1 << i)
        return value
    
    def decode_value(self, value: int) -> Optional[str]:
        """Decode the bitfield value using the decode mapping."""
        if not self.bitfield_decode:
            return None
        
        # Parse the decode string - handle multi-line entries
        # Each decode entry may span multiple lines (e.g., "0x0: text\ncontinued text")
        current_entry = []
        current_value = None
        decode_map = {}
        
        lines = self.bitfield_decode.split('\n')
        
        for line in lines:
            # Check if this line starts a new entry (has "0xN:" at the beginning)
            if line.strip() and ':' in line:
                # Try to parse as a new entry
                parts = line.split(':', 1)
                first_part = parts[0].strip()
                
                # Check if it looks like a value (0x0, 0x1, etc.)
                if first_part.startswith('0x') or (first_part.isdigit()):
                    # Save previous entry if exists
                    if current_value is not None and current_entry:
                        full_text = '\n'.join(current_entry)
                        decode_map[current_value] = full_text
                    
                    # Start new entry
                    try:
                        current_value = int(first_part, 0)
                        current_entry = [line]  # Store the full line including the value prefix
                    except ValueError:
                        # Not a valid value, append to current entry
                        if current_entry:
                            current_entry.append(line)
                else:
                    # Continuation of previous line
                    if current_entry:
                        current_entry.append(line)
            else:
                # Continuation line
                if current_entry:
                    current_entry.append(line)
        
        # Save last entry
        if current_value is not None and current_entry:
            full_text = '\n'.join(current_entry)
            decode_map[current_value] = full_text
        
        result = decode_map.get(value)
        if result:
            # Replace internal newlines with spaces to keep on one line
            result = result.replace('\n', ' ')
            # Strip trailing spaces
            result = result.rstrip()
        return result


class BitfieldDecoder:
    """Main decoder class."""
    
    def __init__(self, default_width: int = 8):
        self.default_width = default_width
        self.mappings: Dict[str, List[BitfieldMapping]] = {}
        self.register_widths: Dict[str, int] = {}
    
    def load_mappings(self, mapping_file: str):
        """Load register mappings from CSV file."""
        with open(mapping_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            
            last_address = None
            last_register_name = None
            last_register_width = None
            next_bit_position = None
            
            for row in reader:
                if len(row) < 7:
                    continue
                
                address = row[0].strip()
                register_name = row[1].strip()
                register_width_str = row[2].strip()
                bitfield_range = row[3].strip()
                bitfield_name = row[4].strip()
                bitfield_description = row[5].strip()
                bitfield_decode = row[6].strip() if len(row) > 6 else ""
                
                # Skip empty rows
                if not address or not bitfield_range:
                    continue
                
                # Handle register width
                if register_width_str:
                    register_width = int(register_width_str)
                elif address == last_address and last_register_width is not None:
                    register_width = last_register_width
                else:
                    register_width = self.default_width
                
                # Store register width
                if address not in self.register_widths:
                    self.register_widths[address] = register_width
                
                # Handle width notation {n}
                if bitfield_range.startswith('{'):
                    width = int(bitfield_range.strip('{}'))
                    if address != last_address or register_name != last_register_name:
                        # New register, start from MSB
                        high_bit = register_width - 1
                        low_bit = high_bit - width + 1
                    else:
                        # Continue from last position
                        if next_bit_position is None:
                            high_bit = register_width - 1
                        else:
                            high_bit = next_bit_position - 1
                        low_bit = high_bit - width + 1
                    
                    bitfield_range = f"{high_bit}:{low_bit}" if high_bit != low_bit else str(high_bit)
                    next_bit_position = low_bit
                else:
                    # Parse the range to update next_bit_position
                    if ':' in bitfield_range:
                        parts = bitfield_range.split(':')
                        low_bit = int(parts[1])
                        next_bit_position = low_bit
                    else:
                        bit = int(bitfield_range)
                        next_bit_position = bit
                
                mapping = BitfieldMapping(
                    address, register_name, register_width,
                    bitfield_range, bitfield_name, bitfield_description,
                    bitfield_decode
                )
                
                if address not in self.mappings:
                    self.mappings[address] = []
                self.mappings[address].append(mapping)
                
                last_address = address
                last_register_name = register_name
                last_register_width = register_width
    
    def format_bitfield_values(self, value: int, mappings: List[BitfieldMapping]) -> str:
        """Format the bitfield values portion of the output."""
        # Check if all bitfields are single bits
        all_single_bits = all(len(m.bit_positions) == 1 for m in mappings)
        
        if all_single_bits:
            # Extract all bit values in order from MSB to LSB
            max_bit = max(max(m.bit_positions) for m in mappings)
            bits = []
            for i in range(max_bit, -1, -1):
                if (value >> i) & 1:
                    bits.append('1')
                else:
                    bits.append('0')
            
            # Group bits by 4s from the LSB side
            bit_string = ''.join(bits)
            grouped = []
            # Reverse to group from LSB
            reversed_bits = bit_string[::-1]
            for i in range(0, len(reversed_bits), 4):
                group = reversed_bits[i:i+4]
                # Reverse back the group
                grouped.append(group[::-1])
            # Reverse the groups to get MSB first
            grouped = grouped[::-1]
            return ','.join(grouped)
        else:
            # Multi-bit fields - format each separately
            parts = []
            sorted_mappings = sorted(mappings, key=lambda m: max(m.bit_positions) if m.bit_positions else 0, reverse=True)
            for mapping in sorted_mappings:
                field_value = mapping.extract_value(value)
                if len(mapping.bit_positions) == 1:
                    parts.append(str(field_value))
                else:
                    # Calculate how many hex digits we need
                    max_val = (1 << len(mapping.bit_positions)) - 1
                    if max_val <= 0xF:
                        parts.append(f"x{field_value:X}")
                    elif max_val <= 0xFF:
                        parts.append(f"x{field_value:02X}")
                    elif max_val <= 0xFFF:
                        parts.append(f"x{field_value:03X}")
                    else:
                        parts.append(f"x{field_value:X}")
            return ', '.join(parts)
    
    def process_registers(self, input_file: str, output_file: str):
        """Process register dump and write decoded output."""
        results = []
        
        with open(input_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            
            for row in reader:
                if len(row) < 2:
                    continue
                
                register = row[0].strip()
                value_str = row[1].strip()
                
                # Parse value (handle hex notation)
                value = int(value_str, 0)
                
                # Get mappings for this register
                if register not in self.mappings:
                    print(f"Warning: No mapping found for register {register}", file=sys.stderr)
                    continue
                
                mappings = self.mappings[register]
                register_name = mappings[0].register_name
                
                # Format the value with bitfield values
                bitfield_values_str = self.format_bitfield_values(value, mappings)
                
                # Determine the hex format for the main value
                # Use uppercase for hex digits, lowercase 'x' for prefix
                if value <= 0xFFFF:
                    value_hex = f"0x{value:X}"
                else:
                    value_hex = f"0x{value:X}"
                
                value_with_bitfields = f"{value_hex} ({bitfield_values_str})"
                
                # Sort mappings by bit position (highest to lowest)
                sorted_mappings = sorted(mappings, key=lambda m: max(m.bit_positions) if m.bit_positions else 0, reverse=True)
                
                # Create one row per bitfield
                for mapping in sorted_mappings:
                    field_value = mapping.extract_value(value)
                    
                    # Format bitfield name with range
                    if ':' in mapping.bitfield_range:
                        bitfield_with_range = f"{mapping.bitfield_name}[{mapping.bitfield_range}]"
                    else:
                        bitfield_with_range = f"{mapping.bitfield_name}[{mapping.bitfield_range}]"
                    
                    # Format the bitfield value (for the "Bitfield Value" column)
                    if len(mapping.bit_positions) == 1:
                        field_value_str = str(field_value)
                    else:
                        # Multi-bit field
                        max_val = (1 << len(mapping.bit_positions)) - 1
                        if max_val <= 0xF:
                            field_value_str = f"0x{field_value:X}"
                        elif max_val <= 0xFF:
                            field_value_str = f"0x{field_value:02X}"
                        elif max_val <= 0xFFF:
                            field_value_str = f"0x{field_value:03X}"
                        else:
                            field_value_str = f"0x{field_value:X}"
                    
                    # Get decoded string
                    decoded = mapping.decode_value(field_value)
                    if decoded is None:
                        decoded = ""
                    
                    results.append([
                        register,
                        register_name,
                        value_with_bitfields,
                        bitfield_with_range,
                        field_value_str,
                        decoded
                    ])
        
        # Write output
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Register', 'Register Name', 'Value (Bitfield Values)', 'Bitfield', 'Bitfield Value', 'Decoding'])
            writer.writerows(results)
        
        print(f"Output written to {output_file}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Decode register bitfields based on mappings')
    parser.add_argument('-o', '--output', help='Output CSV file (default: input filename with _decoded suffix)')
    parser.add_argument('-m', '--map', required=True, help='Register mapping CSV file')
    parser.add_argument('-i', '--inputs', required=True, help='Input register dump CSV file')
    parser.add_argument('-w', '--width', type=int, default=32, 
                        help='Default register width in bits (default: 32)')
    
    args = parser.parse_args()
    
    # Determine output filename if not provided
    if args.output is None:
        import os
        base, ext = os.path.splitext(args.inputs)
        args.output = f"{base}_decoded{ext}"
    
    # Create decoder
    decoder = BitfieldDecoder(default_width=args.width)
    
    # Load mappings
    try:
        decoder.load_mappings(args.map)
    except Exception as e:
        print(f"Error loading mappings: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Process registers
    try:
        decoder.process_registers(args.inputs, args.output)
    except Exception as e:
        print(f"Error processing registers: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
