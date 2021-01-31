#!/usr/bin/python

import sys

def main(args):
    export_module = __import__("xlsx-to-ini-with-ref")
    version = input("Enter version (optional): ")
    print("Generate LIVE ini")
    export_module.main(["xlsx-to-ini-with-ref.py", "global.ini.xlsx", "global.live.ini", "global_ref.ini", version])
    print("Generate PTU ini")
    if version:
        export_module.main(["xlsx-to-ini-with-ref.py", "global.ini.xlsx", "global.ptu.ini", "global_ref_ptu.ini", version + " PTU"])
    else:
        export_module.main(["xlsx-to-ini-with-ref.py", "global.ini.xlsx", "global.ptu.ini", "global_ref_ptu.ini", ""])
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
