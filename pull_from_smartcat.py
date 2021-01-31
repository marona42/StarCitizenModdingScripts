# pull from smartcat project.
# requires export-smartcat.py, smartcat.ini
import configparser
import export_smartcat

config_title='sc_ko'
export_smartcat.main(['pullfs',config_title])
