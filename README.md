# Ath Board Data File tool

Python script to extract/update internal regdb and remove regdomain in ath10k/ath11k BDF files.

## Regdb

Board files with actual regdb can be found on this repository: https://git.codelinaro.org/clo/qsdk/oss/ath11k-bdf/-/tree/NHSS.QSDK.12.4.5

They must be extracted first using `ath11k-bdencoder`: https://github.com/qca/qca-swiss-army-knife

## Usage

### ath10k BDF tool
```
usage: ath10k_bdf_tool.py [-h] -r BDF [-o FILE]

ath10k BDF tool

options:
  -h, --help            show this help message and exit
  -r BDF, --remove-regdomain BDF
                        remove regdomain from ath10k BDF
  -o FILE, --output FILE
                        output file name
```

### ath11k BDF tool
```
usage: ath11k_bdf_tool.py [-h] (-e BDF | -u BDF REGDB | -r BDF) [-o FILE]

ath11k BDF tool

options:
  -h, --help            show this help message and exit
  -e BDF, --extract-regdb BDF
                        extract regdb from ath11k BDF
  -u BDF REGDB, --update-regdb BDF REGDB
                        update regdb in ath11k BDF
  -r BDF, --remove-regdomain BDF
                        remove regdomain from ath11k BDF
  -o FILE, --output FILE
                        output file name
```

## Contributing

Contributions are welcome. Please submit a pull request with any improvements.

## License

This project is licensed under the terms of the MIT license.