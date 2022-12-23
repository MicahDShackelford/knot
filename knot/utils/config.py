import os
import json

from pathlib import Path

import click

from knot.utils.output import dict_to_type


def get_config_path():
    """Gets expected config path."""

    return os.path.abspath(os.path.join(Path.home(), '.knotcli/config.json'))

def check_config(fix: bool = False) -> bool:
    """Checks if a configuration folder exists in your HOME directory."""

    path = get_config_path()

    config_path = os.path.dirname(path)

    # Check config path exists
    if not os.path.exists(config_path):
        if fix: 
            try:
                os.mkdir(config_path)
            except Exception as e:
                # Failure to create config dir, return "invalid"
                return False
        else: 
            # Caller doesn't want this auto-fixed, return "invalid"
            return False

    # Check config file exists
    if not os.path.exists(path):
        if fix: 
            try:
                base_config = dict_to_type({
                    'package': [],
                    'target': [],
                }, 'json', True)

                with open(path, 'w') as f:
                    f.write(base_config)
            except Exception as e:
                # Failure to create config dir, return "invalid"
                return False
        else: 
            # Caller doesn't want this auto-fixed, return "invalid"
            return False
    else: 
        # TODO: check validity of config file
        pass
    
    return True

def put_knot(knot_path: str, overwrite: bool = False):
    """Adds a knot to the users configuration."""

    knot_path = knot_path.rstrip('/')

    # It's not a config, assume its the path to the directory where a .knotrc lives
    if not knot_path.endswith('.knotrc'):
        knot_path = os.path.abspath(os.path.join(knot_path, '.knotrc'))

    # Not a valid knot directory
    if not os.path.exists(knot_path):
        click.echo(
            click.style(
                f"\"{knot_path}\" doesn't exist.\n\nPlease run 'knot init {os.path.dirname(knot_path)}' before trying to install the knot",
                fg="yellow",
            )
        )

        exit(1)

    # Load knot configuration
    try:
        with open(knot_path, 'r') as f:
            knot_config = json.loads(f.read())

    except Exception as e:
        click.echo(
            click.style(
                f"\"{knot_path}\" Failed to load knot at \"{knot_path}\"",
                fg="yellow",
            )
        )

        exit(1)

    user_config_path = get_config_path()

    # Load user configuration
    try:
        with open(user_config_path, 'r') as f:
            user_config = json.loads(f.read())
    
    except Exception as e:
        click.echo(
            click.style(
                f"\"{knot_path}\" Failed to load user configuration at \"{knot_path}\"",
                fg="yellow",
            )
        )

        exit(1)

    knot_name = knot_config.get('name')
    knot_type = knot_config.get('type')

    # Knot already exists
    try:
        if not overwrite and next(k for k in user_config[knot_type] if k.get('name') == knot_name):
            click.echo(
                click.style(
                    f"{knot_name} is already installed, if you would like to overwrite it add the '--overwrite' flag.",
                    fg="yellow",
                )
            )

            exit(1)
    except StopIteration as e: 
        pass

    # Append the configuration to the users knots
    user_config[knot_type].append({
        'name': knot_name,
        'path': os.path.dirname(knot_path),
    })

    # Update user config
    try:
        with open(user_config_path, 'w') as f:
            f.write(dict_to_type(user_config, 'json', True))
    
    except Exception as e:
        click.echo(
            click.style(
                f"Failed to install knot located at \"{knot_path}\"",
                fg="yellow",
            )
        )

        exit(1)
    
    click.echo(
        click.style(
            f"Successfully installed: {knot_name}",
            fg="green",
        )
    )