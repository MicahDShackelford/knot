import os

import click

from pick import pick

from knot import __version__
from knot.utils.output import clear, dict_to_type

@click.command()
@click.argument('path', default=".")
def init(path: str):
    """Initialize a repo to be used by knot."""

    # Path we are initializing
    path = (os.path
        .abspath(os.path.join(os.getcwd(), path))
        .rstrip('/'))

    # Check for existing `.knotrc`
    if os.path.exists(rc_path := os.path.join(path, '.knotrc')):
        click.echo(
            click.style(
                f"\"{rc_path}\" already exists, cannot reinitialize",
                fg="yellow",
            )
        )

        exit(1)

    # Collect initialization values & ensure its what the user wanted
    while True:
        values = _collect_init_values(path)

        click.echo(f"About to write to \"{rc_path}\"\n\n" + (pretty_values := dict_to_type(values, 'json', pretty=True)) + "\n")

        if input('Is this okay (yes)? ').strip().lower() in ['', 'yes']:
            break
    
    # Write to rc file
    with open(rc_path, 'w') as f:
        f.write(pretty_values)

def _collect_init_values(path: str) -> dict:
    """Collects required knotrc values."""

    values = {}

    prompts = [
        # Names will be used when referencing 
        {
            'prompt': 'What would you like this knot to be called?',
            'key': "name",
            'type': "text",
            'default': os.path.basename(path)
        },
        # Language/package manager for this knot
        {
            'prompt': 'What language/package manager is being used?',
            'key': "language",
            'type': "select",
            'options': ["nodejs/npm", "php/composer"],
        },
        # If this knot is the source or target
        {
            'prompt': 'Is this a package or target?',
            'key': "type",
            'type': "select",
            'options': ["package", "target"]
        },
        # Utilize symlinks 
        #
        # Not using symlinks will simply sync the changes 
        # from package to target, maintaining a copy in both 
        # folders, this is useful where targets might be 
        # mounted and not have access the host symlinks
        {
            'prompt': 'Would you like to use symlinks when linking this package?',
            'key': "use_symlink",
            'type': "select",
            'options': ["yes", "no"],
            'cast': 'bool',
            'if': (lambda v: v.get('type') == 'package')
        },
        # Watch command to build
        {
            'prompt': 'What is the build watcher command (ex. npm run watch)?',
            'key': "build_command",
            'type': "text",
            'if': (lambda v: v.get('language') == 'nodejs/npm')
        },
        # The version of knot this configuration was created on
        {
            "key": "knot_version",
            "type": "static",
            "value": __version__
        }
    ]

    clear()

    for prompt in prompts:
        # This prompt should only be asked if some condition is met
        if (fn := prompt.get('if')) and not fn(values):
            continue 

        # Reusable stuff for many prompt types
        prompt_text = prompt.get('prompt')
        prompt_key = prompt.get('key')
        prompt_type = prompt.get('type')

        # Set default if prompt specifies one
        if default := prompt.get('default'):
            prompt_text += f" ({default})"

        # Collect responses
        if prompt_type == 'select':
            values[prompt_key] = pick(prompt.get('options'), prompt_text, indicator="->")[0]
        elif prompt_type == 'text':
            click.echo(f" {prompt_text}\n")
            values[prompt_key] = input(' ') or default
        elif prompt_type == 'static':
            values[prompt_key] = prompt.get('value')

        # Handle custom casting
        if cast_to := prompt.get('cast'):
            if cast_to == 'bool':
                if values[prompt_key].lower() in ['yes', 'y']:
                    values[prompt_key] = True
                else:
                    values[prompt_key] = False

        clear()
        
    return values