import csv
import os
import argparse
import sys


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description="Update TCG Marketplace Price from TCG Market Price in a CSV file."
    )
    parser.add_argument("--file", "-f", required=True, help="Input CSV file path")
    parser.add_argument(
        "--price-floor", "-pf", required=True, type=float, help="Price floor (decimal)"
    )
    return parser.parse_args(argv)


def process_row(row, price_floor, row_num):
    tcg_low_price = row["TCG Low Price"]
    try:
        low_price = float(tcg_low_price)
    except (ValueError, TypeError):
        card_name = row["Product Name"]
        raise ValueError(
            f"Malformed or missing TCG Low Price at row {row_num} with name {card_name}."
        )
    if low_price >= price_floor:
        row["TCG Marketplace Price"] = f"{low_price:.2f}"
    else:
        row["TCG Marketplace Price"] = f"{price_floor:.2f}"
    return row


def read_and_update_csv(input_csv, price_floor):
    output_csv = os.path.splitext(input_csv)[0] + "_updated.csv"
    try:
        with open(input_csv, newline="", encoding="utf-8") as infile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames
            if not fieldnames:
                print("Error: CSV file missing header.")
                return 1
            if (
                "TCG Market Price" not in fieldnames
                or "TCG Marketplace Price" not in fieldnames
            ):
                print("Error: Required columns missing in CSV header.")
                return 1
            rows = []
            for i, row in enumerate(reader, 2):
                try:
                    updated_row = process_row(row, price_floor, i)
                except ValueError as e:
                    print(f"Error: {e}")
                    return 1
                rows.append(updated_row)
        with open(output_csv, "w", newline="", encoding="utf-8") as outfile:
            writer = csv.DictWriter(
                outfile, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL
            )
            writer.writeheader()
            writer.writerows(rows)
        print(f"Output written to {output_csv}")
        return 0
    except FileNotFoundError:
        print(f"Error: File not found: {input_csv}")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1


def main(argv):
    args = parse_args(argv)
    return read_and_update_csv(args.file, args.price_floor)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
