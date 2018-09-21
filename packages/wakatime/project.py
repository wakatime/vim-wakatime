# -*- coding: utf-8 -*-
"""
    wakatime.project
    ~~~~~~~~~~~~~~~~

    Returns a project for the given file.

    :copyright: (c) 2013 Alan Hamlett.
    :license: BSD, see LICENSE for more details.
"""

import os
import logging
import random

from .compat import open
from .projects.git import Git
from .projects.mercurial import Mercurial
from .projects.projectfile import ProjectFile
from .projects.projectmap import ProjectMap
from .projects.subversion import Subversion


log = logging.getLogger('WakaTime')


# List of plugin classes to find a project for the current file path.
CONFIG_PLUGINS = [
    ProjectFile,
    ProjectMap,
]
REV_CONTROL_PLUGINS = [
    Git,
    Mercurial,
    Subversion,
]


def get_project_info(configs, heartbeat, data):
    """Find the current project and branch.

    First looks for a .wakatime-project file. Second, uses the --project arg.
    Third, uses the folder name from a revision control repository. Last, uses
    the --alternate-project arg.

    Returns a project, branch tuple.
    """

    project_name, branch_name = heartbeat.project, heartbeat.branch

    if heartbeat.type != 'file':
        project_name = project_name or heartbeat.args.project or heartbeat.args.alternate_project
        return project_name, branch_name

    if project_name is None or branch_name is None:

        for plugin_cls in CONFIG_PLUGINS:

            plugin_name = plugin_cls.__name__.lower()
            plugin_configs = get_configs_for_plugin(plugin_name, configs)

            project = plugin_cls(heartbeat.entity, configs=plugin_configs)
            if project.process():
                project_name = project_name or project.name()
                branch_name = project.branch()
                break

    if project_name is None:
        project_name = data.get('project') or heartbeat.args.project

    hide_project = heartbeat.should_obfuscate_project()

    if project_name is None or branch_name is None:

        for plugin_cls in REV_CONTROL_PLUGINS:

            plugin_name = plugin_cls.__name__.lower()
            plugin_configs = get_configs_for_plugin(plugin_name, configs)

            project = plugin_cls(heartbeat.entity, configs=plugin_configs)
            if project.process():
                project_name = project_name or project.name()
                branch_name = branch_name or project.branch()
                if hide_project:
                    branch_name = None
                    project_name = generate_project_name()
                    project_file = os.path.join(project.folder(), '.wakatime-project')
                    try:
                        with open(project_file, 'w') as fh:
                            fh.write(project_name)
                    except IOError:
                        project_name = None
                break

    if project_name is None and not hide_project:
        project_name = data.get('alternate_project') or heartbeat.args.alternate_project

    return project_name, branch_name


def get_configs_for_plugin(plugin_name, configs):
    if configs and configs.has_section(plugin_name):
        return dict(configs.items(plugin_name))
    return None


def generate_project_name():
    """Generates a random project name."""

    adjectives = [
        'aged', 'ancient', 'autumn', 'billowing', 'bitter', 'black', 'blue', 'bold',
        'broad', 'broken', 'calm', 'cold', 'cool', 'crimson', 'curly', 'damp',
        'dark', 'dawn', 'delicate', 'divine', 'dry', 'empty', 'falling', 'fancy',
        'flat', 'floral', 'fragrant', 'frosty', 'gentle', 'green', 'hidden', 'holy',
        'icy', 'jolly', 'late', 'lingering', 'little', 'lively', 'long', 'lucky',
        'misty', 'morning', 'muddy', 'mute', 'nameless', 'noisy', 'odd', 'old',
        'orange', 'patient', 'plain', 'polished', 'proud', 'purple', 'quiet', 'rapid',
        'raspy', 'red', 'restless', 'rough', 'round', 'royal', 'shiny', 'shrill',
        'shy', 'silent', 'small', 'snowy', 'soft', 'solitary', 'sparkling', 'spring',
        'square', 'steep', 'still', 'summer', 'super', 'sweet', 'throbbing', 'tight',
        'tiny', 'twilight', 'wandering', 'weathered', 'white', 'wild', 'winter', 'wispy',
        'withered', 'yellow', 'young'
    ]
    nouns = [
        'art', 'band', 'bar', 'base', 'bird', 'block', 'boat', 'bonus',
        'bread', 'breeze', 'brook', 'bush', 'butterfly', 'cake', 'cell', 'cherry',
        'cloud', 'credit', 'darkness', 'dawn', 'dew', 'disk', 'dream', 'dust',
        'feather', 'field', 'fire', 'firefly', 'flower', 'fog', 'forest', 'frog',
        'frost', 'glade', 'glitter', 'grass', 'hall', 'hat', 'haze', 'heart',
        'hill', 'king', 'lab', 'lake', 'leaf', 'limit', 'math', 'meadow',
        'mode', 'moon', 'morning', 'mountain', 'mouse', 'mud', 'night', 'paper',
        'pine', 'poetry', 'pond', 'queen', 'rain', 'recipe', 'resonance', 'rice',
        'river', 'salad', 'scene', 'sea', 'shadow', 'shape', 'silence', 'sky',
        'smoke', 'snow', 'snowflake', 'sound', 'star', 'sun', 'sun', 'sunset',
        'surf', 'term', 'thunder', 'tooth', 'tree', 'truth', 'union', 'unit',
        'violet', 'voice', 'water', 'waterfall', 'wave', 'wildflower', 'wind', 'wood'
    ]
    numbers = [str(x) for x in range(10)]
    return ' '.join([
        random.choice(adjectives).capitalize(),
        random.choice(nouns).capitalize(),
        random.choice(numbers) + random.choice(numbers),
    ])
