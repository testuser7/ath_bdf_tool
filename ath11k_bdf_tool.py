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

# usage: ath11k_bdf_tool.py [-h] (-e BDF | -u BDF REGDB | -r BDF) [-o FILE]
#
# ath11k BDF tool
#
# options:
#   -h, --help            show this help message and exit
#   -e BDF, --extract-regdb BDF
#                         extract regdb from ath11k BDF
#   -u BDF REGDB, --update-regdb BDF REGDB
#                         update regdb in ath11k BDF
#   -r BDF, --remove-regdomain BDF
#                         remove regdomain from ath11k BDF
#   -o FILE, --output FILE
#                         output file name

import io
from argparse import ArgumentParser
from hashlib import md5
from mmap import mmap, ACCESS_COPY
from struct import pack, unpack, iter_unpack

CHECKSUM_ADDR = 0xa

BDF_HEADER = '010004040000'

REGDB_HEADER = '000004003700'
REGDB_FILE = 'regdb.bin'
REGDB_BDF = {
    0x127c8: 'IPQ5018/QCN6122',
    0x10f48: 'IPQ5018/QCN6122(old)',
    0xae2e: 'IPQ6018',
    0x1978e: 'IPQ8074',
    0x12df0: 'IPQ9574',
    0x12dee: 'QCN9074',
}

REGDOMAIN_CODE = '0000'
REGDOMAIN_ADDR = [
    0x34, 
    0x450, 
    0x458, 
    0x500, 
    0x5a8
]


def calculate_checksum(checksum, data, new_data):
    result = unpack('>H', checksum)[0]

    for data_byte in iter_unpack('>H', data + new_data):
        result = result ^ data_byte[0]

    return(pack('>H', result))


def cmd_extract_regdb(args):
    with io.open(args.extract_regdb, 'rb') as b:
        bdf = mmap(b.fileno(), 0, access=ACCESS_COPY)

        if bdf[0:6] != bytes.fromhex(BDF_HEADER):
            exit('Not valid ath11k BDF file')

        regdb_addr = bdf.find(bytes.fromhex(REGDB_HEADER))

        if regdb_addr == -1:
            exit('Unable to find regdb in BDF')

        regdb_size = bdf[regdb_addr - 3] * 0x100

        print(f'Extracting regdb from {REGDB_BDF.get(regdb_addr, "unknown")} BDF')

        with io.open(args.output or REGDB_FILE, 'wb') as r:
            r.write(bdf[regdb_addr:regdb_addr + regdb_size])


def cmd_update_regdb(args):
    with io.open(args.update_regdb[0], 'rb') as b:
        bdf = mmap(b.fileno(), 0, access=ACCESS_COPY)

        if bdf[0:6] != bytes.fromhex(BDF_HEADER):
            exit('Not valid ath11k BDF file')

        regdb_addr = bdf.find(bytes.fromhex(REGDB_HEADER))

        if regdb_addr == -1:
            exit('Unable to find regdb in BDF')

        regdb_size = bdf[regdb_addr - 3] * 0x100

        with io.open(args.update_regdb[1], 'rb') as r:
            regdb = mmap(r.fileno(), 0, access=ACCESS_COPY)

            if regdb[0:6] != bytes.fromhex(REGDB_HEADER):
                exit('Not valid ath11k regdb file')

            if len(regdb) != regdb_size:
                exit(f'Incorrect regdb file size (should be {regdb_size}B)')

            if md5(regdb).hexdigest() != md5(bdf[regdb_addr:regdb_addr + regdb_size]).hexdigest():
                checksum = bdf[CHECKSUM_ADDR:CHECKSUM_ADDR + 2]
                checksum = calculate_checksum(checksum, bdf[regdb_addr:regdb_addr + regdb_size], regdb)
                bdf[CHECKSUM_ADDR:CHECKSUM_ADDR + 2] = checksum
                bdf[regdb_addr:regdb_addr + regdb_size] = regdb
                bdf_file = bdf.read()
                bdf.close()

                print(f'Updating regdb in {REGDB_BDF.get(regdb_addr, "unknown")} BDF')

                with io.open(args.output or args.update_regdb[0], 'wb') as bdf:
                    bdf.write(bdf_file)
            else:
                print('Regdb is up to date')


def cmd_remove_regdomain(args):
    with io.open(args.remove_regdomain, 'rb') as b:
        bdf = mmap(b.fileno(), 0, access=ACCESS_COPY)

        if bdf[0:6] != bytes.fromhex(BDF_HEADER):
            exit('Not valid ath11k BDF file')

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
    parser = ArgumentParser(description='ath11k BDF tool')

    cmd_group = parser.add_mutually_exclusive_group(required=True)
    cmd_group.add_argument('-e', '--extract-regdb', metavar='BDF',
                           help='extract regdb from ath11k BDF')
    cmd_group.add_argument('-u', '--update-regdb', metavar=('BDF', 'REGDB'), nargs=2,
                           help='update regdb in ath11k BDF')
    cmd_group.add_argument('-r', '--remove-regdomain', metavar='BDF',
                           help='remove regdomain from ath11k BDF')

    parser.add_argument('-o', '--output', metavar='FILE',
                        help='output file name')

    args = parser.parse_args()

    if args.extract_regdb:
        return cmd_extract_regdb(args)
    elif args.update_regdb:
        return cmd_update_regdb(args)
    elif args.remove_regdomain:
        return cmd_remove_regdomain(args)


if __name__ == '__main__':
    main()