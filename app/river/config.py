import os
import ConfigParser

config = ConfigParser.ConfigParser(allow_no_value=True)
config.readfp(open('defaults.cfg'))
config.read(['river.cfg', os.path.expanduser('~/.config/river')])
