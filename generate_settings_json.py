"""
This script is used to generate the json settings file.
"""

import json

# Settings data as python dictionary
data = {'WindowWidth': 960,
        'WindowHeight': 720,
        'db_path': 'body_weight_db.csv',
        'font_point_size': 14,
        'database_path': 'body_weight_db.csv'}

# Export to json format
with open('settings.json', 'w') as f:
    json.dump(data, f, indent=4, sort_keys=True)
