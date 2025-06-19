#run git -C C:/wayzz-web log --pretty=format:"%h›%an›%ad›%s" --date=format:"%Y-%m-%d %H:%M" > wayzz_web_logs.csv
import utils as utils
import csv
import os
import sys
import datetime
import time
import re
import pandas as pd
import numpy as np
import yaml

# Get the current working directory
cwd = os.getcwd()

# Import config yaml file
with open(cwd + '/config.yaml') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

# load config {'repository': ['C:/mwss/', 'C:/wayzz-web/']}
repositories = config['repositories']


# for each repo
for path in repositories:
    utils.run_command('git -C '+path+' log --pretty=format:"%h›%an›%ad›%s" --date=format:"%Y-%m-%d %H:%M" > wayzz_web_logs.csv')

