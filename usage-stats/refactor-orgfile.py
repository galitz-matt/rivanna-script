#!/usr/bin/env python

import argparse
import shutil
import sys
import re
import tempfile

lookup = {
	"BATT": "BA",
	"BII": "BI",
	"CLAS": "AS",
	"COMM": "MC",
	"DARD": "DA",
	"ITS/RC": "RC",
	"LAW": "LW",
	"PROV/VPR": "PV",
	"SDS": "DS",
	"SEAS": "EN",
	"SEHD": "ED",
	"SOM": "MD",
	"SCPS": "CP",
	"ARCH": "AR",
	"NURS": "NR",
	"Other": "Other"
}


def init_parser() -> argparse.ArgumentParser:
	parser = argparse.ArgumentParser(description="Process organization file")
	parser.add_argument("organization_file", help="Path to the organization file", type=str)
	return parser


def main(organization_file: str) -> None:
	pattern = re.compile(r"\s+")
	with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
		with open(organization_file, 'r') as file:
			for line in file:
				if "-----" not in line:
					organization, code = pattern.split(line.strip())
					temp_file.write(
						f"{organization} {lookup.get(code, code)}\n")  
	shutil.move(temp_file.name, organization_file)


if __name__ == "__main__":
	parser = init_parser()
	args = parser.parse_args()
	try:
		main(args.organization_file)
	except Exception as e:
		print(f"Error: {e}")
		sys.exit(1)
