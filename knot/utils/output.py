import os
import json
import yaml
import logging

import click


def dict_to_type(dictionary: dict, type: str, pretty: bool = False) -> str:
    """Outputs a dictionary in a desired format (yaml/json)."""

    if type == 'yaml':
        # Output dictionary to yaml
        return (yaml
            .dump(dictionary)
            .rstrip())    
    elif type == 'json':
        # Output dictionary to json
        return json.dumps(dictionary, indent=4 if pretty else None)
    else:
        if logging.getLogger().getEffectiveLevel() >= 40:
            logging.error(f"Invalid output type \"{type}\" specified, valid options are: \"yaml\" or \"json\"")

        return dictionary

def clear():
    os.system('cls' if os.name == 'nt' else 'echo -e \\\\033c')