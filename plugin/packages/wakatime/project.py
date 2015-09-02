# -*- coding: utf-8 -*-
"""
    wakatime.project
    ~~~~~~~~~~~~~~~~

    Returns a project for the given file.

    :copyright: (c) 2013 Alan Hamlett.
    :license: BSD, see LICENSE for more details.
"""

import logging

from .projects.git import Git
from .projects.mercurial import Mercurial
from .projects.projectmap import ProjectMap
from .projects.subversion import Subversion
from .projects.wakatime_project_file import WakaTimeProjectFile


log = logging.getLogger('WakaTime')


# List of plugin classes to find a project for the current file path.
CONFIG_PLUGINS = [
    WakaTimeProjectFile,
    ProjectMap,
]
REV_CONTROL_PLUGINS = [
    Git,
    Mercurial,
    Subversion,
]


def get_project_info(configs, args):
    """Find the current project and branch.

    First looks for a .wakatime-project file. Second, uses the --project arg.
    Third, uses the folder name from a revision control repository. Last, uses
    the --alternate-project arg.

    Returns a project, branch tuple.
    """

    project_name, branch_name = None, None

    for plugin_cls in CONFIG_PLUGINS:

        plugin_name = plugin_cls.__name__.lower()
        plugin_configs = get_configs_for_plugin(plugin_name, configs)

        project = plugin_cls(args.entity, configs=plugin_configs)
        if project.process():
            project_name = project_name or project.name()
            branch_name = project.branch()
            break

    if project_name is None:
        project_name = args.project

    if project_name is None or branch_name is None:

        for plugin_cls in REV_CONTROL_PLUGINS:

            plugin_name = plugin_cls.__name__.lower()
            plugin_configs = get_configs_for_plugin(plugin_name, configs)

            project = plugin_cls(args.entity, configs=plugin_configs)
            if project.process():
                project_name = project_name or project.name()
                branch_name = branch_name or project.branch()
                break

    if project_name is None:
        project_name = args.alternate_project

    return project_name, branch_name


def get_configs_for_plugin(plugin_name, configs):
    if configs and configs.has_section(plugin_name):
        return dict(configs.items(plugin_name))
    return None
