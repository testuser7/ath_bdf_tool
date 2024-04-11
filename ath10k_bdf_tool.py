#! /usr/bin/python

'''
The MIT License (MIT)

Copyright (c) 2024 Paweł Owoc

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
'''

# usage: ath10k_bdf_tool.py [-h] -r BDF [-o FILE]
#
# ath10k BDF tool
#
# options:
#   -h, --help            show this help message and exit
#   -r BDF, --remove-regdomain BDF
#                         remove regdomain from ath10k BDF
#   -o FILE, --output FILE
#                         output file name

import io
from argparse import ArgumentParser
from mmap import mmap, ACCESS_COPY
from struct import pack, unpack, iter_unpack

CHECKSUM_ADDR = 0x2

BDF_HEADER = '202f'

REGDOMAIN_CODE = '0000'
REGDOMAIN_ADDR = [
    0xc
]


def calculate_checksum(checksum, data, new_data):
    result = unpack('>H', checksum)[0]

    for data_byte in iter_unpack('>H', data + new_data):
        result = result ^ data_byte[0]

    return(pack('>H', result))


def cmd_remove_regdomain(args):
    with io.open(args.remove_regdomain, 'rb') as b:
        bdf = mmap(b.fileno(), 0, access=ACCESS_COPY)

        if bdf[0:2] != bytes.fromhex(BDF_HEADER):
            exit('Not valid ath10k BDF file')

        regdomain = bdf[REGDOMAIN_ADDR[0]:REGDOMAIN_ADDR[0] + 2]
        no_regdomain = bytes.fromhex(REGDOMAIN_CODE)

        if regdomain != no_regdomain:
            checksum = bdf[CHECKSUM_ADDR:CHECKSUM_ADDR + 2]
            print(f'Remove regdomain 0x{bytes(reversed(regdomain)).hex()}')
            for addr in REGDOMAIN_ADDR:
                if bdf[addr:addr + 2] == regdomain:
                    checksum = calculate_checksum(checksum, bdf[addr:addr + 2], no_regdomain)
                    bdf[addr:addr + 2] = no_regdomain

            bdf[CHECKSUM_ADDR:CHECKSUM_ADDR + 2] = checksum
            bdf_file = bdf.read()
            bdf.close()

            with io.open(args.output or args.remove_regdomain, 'wb') as bdf:
                bdf.write(bdf_file)
        else:
            print('Regdomain is not set')


def main():
    parser = ArgumentParser(description='ath10k BDF tool')

    cmd_group = parser.add_mutually_exclusive_group(required=True)
    cmd_group.add_argument('-r', '--remove-regdomain', metavar='BDF',
                           help='remove regdomain from ath10k BDF')

    parser.add_argument('-o', '--output', metavar='FILE',
                        help='output file name')

    args = parser.parse_args()

    if args.remove_regdomain:
        return cmd_remove_regdomain(args)


if __name__ == '__main__':
    main()