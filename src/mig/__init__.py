# beautified imports
# from .backend.configurationhandler import ConfigurationFile
# from .backend.dhsipcaller import DSHIPHeader
# from .backend.runseasave import RunSeasave
# from .frontend.main import *
from .backend import *
from .frontend import *
# necessary imports
import logging
import logging.config
import yaml
from pathlib import Path

# try:
#     with open('logging.yaml') as yaml_config:
#         log_config_dict = yaml.safe_load(yaml_config)
# except yaml.YAMLError as error:
#     print(f'Configuration file could not be loaded: {error}')
# except FileNotFoundError as error:
#     print(f'Configuration file could not be found: {error}')
#     print('Trying to load absolute path...')
#     try:
#         absolute_path = Path('src', 'mig', 'logging.yaml')
#         with open(absolute_path) as yaml_config:
#             log_config_dict = yaml.safe_load(yaml_config)
#         print(f'Successfully loaded config file at {absolute_path}')
#     except FileNotFoundError as error:
#         print(f'Could find the config file nowhere: {error}')
#
# else:
#     try:
#         logging.config.dictConfig(log_config_dict)
#     except ValueError as error:
#         print(f'Configuration file is not properly formated: {error}')
# # TODO: add default behaviour inside the excepts?
