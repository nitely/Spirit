#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import functools
import argparse
from importlib import import_module
from subprocess import call


def create_project(project_name, path, exit_err):
    try:
        import_module(project_name)
    except ImportError:
        pass
    else:
        exit_err(
            "'%s' conflicts with the name of an existing "
            "Python module and cannot be used as a project "
            "name" % project_name)

    extra_path = os.path.dirname(os.path.dirname(__file__))
    template_path = os.path.join(extra_path, 'project_template')

    command = [
        'django-admin',
        'startproject',
        '--template=' + template_path,
        project_name]

    if path:
        command.append(path)

    print('Creating spirit project...')

    if call(command) != 0:
        exit_err(
            "Tried to run \"%s\" but it "
            "returned an error "
            "(should be printed above)\n" % ' '.join(command))

    print('ok')


def execute_from_command_line():
    parser = argparse.ArgumentParser(description='Spirit commands')
    subparsers = parser.add_subparsers(help='sub-command help')
    start_parser = subparsers.add_parser(
        'startproject', help='creates a Spirit project directory structure')
    start_parser.add_argument(
        'project_name', help='name of the project')
    start_parser.add_argument(
        '--path', default=None, help='optional destination directory')
    args = parser.parse_args()
    create_project(
        project_name=args.project_name,
        path=args.path,
        exit_err=functools.partial(parser.exit, 1))


def main():
    execute_from_command_line()


if __name__ == "__main__":
    main()
