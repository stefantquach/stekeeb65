import re
import sys
import argparse

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('-r', '--reference', help="reference file")
parser.add_argument('-f', '--file', help="file to apply layout to")

args = parser.parse_args()

ref_filename = args.reference
app_filename = args.file

ref_header_regex = r"module MX_Alps_Hybrid:MX-([0-9\.]+)U-NoLED \(layer F.Cu\)"
at_regex = r"\(at ([0-9\.]+) ([0-9\.]+)\)"
key_regex = r"\(fp_text reference (K_[0-9]+)"

# generate dictionary of names
position_dict = {}
with open(ref_filename, "r") as ref_file:
    state = 0
    position = (None,None)
    for line in ref_file:
        # find the header
        if state == 0:
            headers = re.search(ref_header_regex, line)
            if (headers is not None):
                state = 1

        # find the at line
        elif state == 1:
            pos_search = re.search(at_regex, line)
            if pos_search is not None and pos_search.group(1) is not None and pos_search.group(2) is not None:
                position = (float(pos_search.group(1)), float(pos_search.group(2)))
                state = 2

        # find the key
        elif state == 2:
            key_search = re.search(key_regex, line)
            if key_search is not None and key_search.group(1) is not None:
                position_dict[key_search.group(1)] = position

                # reset machine
                position = (None, None)
                state = 0

print(position_dict)

# apply the changes