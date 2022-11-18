import re
import sys
import argparse

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('-r', '--reference', help="reference file")
parser.add_argument('-f', '--file', help="file to apply layout to")

args = parser.parse_args()

ref_filename = args.reference
app_filename = args.file

ref_header_regex = r"module MX_Alps_Hybrid:MX-([0-9\.]+)U"
out_header_regex = r"footprint \"MX_Hotswap:MX-Hotswap-([0-9\.]+)U"
led_header_regex = r"footprint \"random-keyboard-parts:QBLP677R-RGB\""
at_regex = r"\(at ([0-9\.]+) ([0-9\.]+)\)"
key_regex = r"(K_[0-9]+)"
led_regex = r"(D_[0-9]+)"

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

# find the lines where the changes need to go
key_line_dict = {}
with open(app_filename) as app_file:
    lines = app_file.readlines()

    # find all the lines for every key
    state = 0
    state1 = 0
    save_line = None
    save_line1 = None
    for (line_num, line) in enumerate(lines):
        # print(line)
        # find the header
        if state == 0:
            headers = re.search(out_header_regex, line)
            if (headers is not None):
                state = 1

        # find the at line
        elif state == 1:
            pos_search = re.search(at_regex, line)
            if pos_search is not None and pos_search.group(1) is not None and pos_search.group(2) is not None:
                save_line = line_num
                state = 2

        # find the key
        elif state == 2:
            key_search = re.search(key_regex, line)
            if key_search is not None and key_search.group(1) is not None:
                key_line_dict[key_search.group(1)] = save_line

                # reset machine
                save_line1 = None
                state = 0

        ###########
        # # find the header
        # if state1 == 0:
        #     headers = re.search(led_header_regex, line)
        #     if (headers is not None):
        #         state1 = 1

        # # find the at line
        # elif state1 == 1:
        #     pos_search = re.search(at_regex, line)
        #     if pos_search is not None and pos_search.group(1) is not None and pos_search.group(2) is not None:
        #         save_line = line_num
        #         state1 = 2

        # # find the key
        # elif state1 == 2:
        #     key_search = re.search(led_regex, line)
        #     if key_search is not None and key_search.group(1) is not None:
        #         key_line_dict[key_search.group(1)] = save_line

        #         # reset machine
        #         save_line1 = None
        #         state1 = 0

    print("\n") 
    print(key_line_dict)

# Apply changes
with open(app_filename, "w") as app_file:
    # apply change to every line
    for key in key_line_dict:
        position = position_dict[key]
        lines[key_line_dict[key]] = "    (at %.4f %.4f)\n" % (position[0], position[1])

    app_file.writelines(lines)


