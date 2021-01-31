#!/usr/bin/python

import sys

def main(args):
    export_module = __import__("xlsx-to-ini-with-ref")
    export_module.main(["xlsx-to-ini-with-ref.py", "global.ini.xlsx", "global.ini", "global_ref_ptu.ini"])
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
