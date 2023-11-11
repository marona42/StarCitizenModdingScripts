# pull from smartcat project to baked ini file.
# pull from smartcat by downloading .xlsx file, and then convert it to .ini file.
# requires export-smartcat.py, smartcat.ini
import sys
import export_smartcat
import xlsx_to_ini


def main(args):
    config_title = "sc_ko_m"
    docs = export_smartcat.main(["pullfs", config_title])  # [[doc id,이름],...]

    xlsx_to_ini.main(docs)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
