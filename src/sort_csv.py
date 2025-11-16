#!/usr/bin/env python3
"""
Script to sort rows in a CSV file by the Input column according to a predefined order.
"""
import argparse
import csv
import sys


# Define the sort order for the Input column
SORT_ORDER = [
    "path_1", "path_2", "path_3", "path_4", "path_5",
    "path_6", "path_7", "path_8", "path_9", "path_10",
    "path_11", "path_12", "path_13", "path_14", "path_15",
    "path_16", "path_17", "path_18", "path_19", "path_20",
    "path_21", "path_22", "path_23", "path_24", "path_25",
    "cycle_3", "cycle_4", "cycle_5", "cycle_6", "cycle_7",
    "cycle_8", "cycle_9", "cycle_10", "cycle_11", "cycle_12",
    "cycle_13", "cycle_14", "cycle_15", "cycle_16", "cycle_17",
    "cycle_18", "cycle_19", "cycle_20", "cycle_21", "cycle_22",
    "cycle_23", "cycle_24", "cycle_25",
    "ladder_1", "ladder_2", "ladder_3", "ladder_4", "ladder_5",
    "ladder_6", "ladder_7", "ladder_8", "ladder_9", "ladder_10",
    "ladder_11", "ladder_12", "ladder_13", "ladder_14", "ladder_15",
    "book_1", "book_2", "book_3", "book_4", "book_5",
    "book_6", "book_7", "book_8", "book_9", "book_10",
    "book_11", "book_12", "book_13", "book_14", "book_15",
    "friendship_1", "friendship_2", "friendship_3", "friendship_4", "friendship_5",
    "friendship_6", "friendship_7", "friendship_8", "friendship_9", "friendship_10",
    "friendship_11", "friendship_12", "friendship_13", "friendship_14", "friendship_15",
    "trisnake_1", "trisnake_2", "trisnake_3", "trisnake_4", "trisnake_5",
    "trisnake_6", "trisnake_7", "trisnake_8", "trisnake_9", "trisnake_10",
    "trisnake_11", "trisnake_12", "trisnake_13", "trisnake_14", "trisnake_15",
    "c4snake_1", "c4snake_2", "c4snake_3", "c4snake_4", "c4snake_5",
    "c4snake_6", "c4snake_7", "c4snake_8", "c4snake_9", "c4snake_10",
    "c4snake_11", "c4snake_12", "c4snake_13", "c4snake_14", "c4snake_15",
    "c6snake_1", "c6snake_2", "c6snake_3", "c6snake_4", "c6snake_5",
    "c6snake_6", "c6snake_7", "c6snake_8", "c6snake_9", "c6snake_10",
    "c6snake_11", "c6snake_12", "c6snake_13", "c6snake_14", "c6snake_15",
    "bintree_0", "bintree_1", "bintree_2", "bintree_3", "bintree_4",
    "bintree_5", "bintree_6", "bintree_7",
]

# Create dictionary to map Input values to sort indices
SORT_ORDER_DICT = {value: index for index, value in enumerate(SORT_ORDER)}


def get_sort_key(input_value):
    """
    Return the sort index for an Input value.
    If the value is not in SORT_ORDER, return a large value to place it at the end.
    """
    return SORT_ORDER_DICT.get(input_value, len(SORT_ORDER))


def sort_csv(input_file, output_file=None):
    """
    Read CSV file, sort rows by Input column, and write back.
    
    Args:
        input_file: Path to input CSV file
        output_file: Path to output CSV file (default is to overwrite input file)
    """
    try:
        # Read CSV file
        with open(input_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            # Check if Input column exists
            if 'Input' not in rows[0].keys() if rows else {}:
                print(f"Error: CSV file does not have 'Input' column", file=sys.stderr)
                sys.exit(1)
            
            # Sort rows by Input column
            sorted_rows = sorted(rows, key=lambda row: get_sort_key(row['Input']))
        
        # Determine output file
        if output_file is None:
            output_file = input_file
        
        # Write sorted CSV file
        fieldnames = reader.fieldnames
        if fieldnames is None:
            print(f"Error: CSV file has no header row", file=sys.stderr)
            sys.exit(1)
        
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(sorted_rows)
        
        print(f"Sorted {len(sorted_rows)} rows and saved to {output_file}")
        
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='Sort rows in CSV file by Input column'
    )
    parser.add_argument(
        '--input',
        required=True,
        help='Path to input CSV file'
    )
    parser.add_argument(
        '--output',
        default=None,
        help='Path to output CSV file (default is to overwrite input file)'
    )
    
    args = parser.parse_args()
    sort_csv(args.input, args.output)


if __name__ == '__main__':
    main()
