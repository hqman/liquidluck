#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import argparse
import logging
from liquidluck.options import enable_pretty_logging
from liquidluck.options import g, settings
from liquidluck.utils import import_object, walk_dir

from liquidluck.writers.base import load_jinja
from liquidluck.readers import alias as reader_alias


def load_settings(path):
    config = {}
    execfile(path, {}, config)

    for key in config:
        settings[key] = config[key]

    g.source_directory = os.path.abspath(settings.source)
    g.output_directory = os.path.abspath(settings.output)
    g.static_directory = os.path.abspath(settings.static_output)
    logging.info('Load Settings Finished')

    load_jinja()


def load_posts(path):
    readers = []
    for reader in settings.readers:
        if reader in reader_alias:
            reader = reader_alias[reader]
        readers.append(import_object(reader))

    def detect_reader(filepath):
        for Reader in readers:
            reader = Reader(filepath)
            if reader.support():
                return reader.render()
        return None

    for filepath in walk_dir(path):
        post = detect_reader(filepath)
        if not post:
            g.pure_files.append(filepath)
        elif not post.date:
            g.pure_pages.append(post)
        elif post.public:
            g.public_posts.append(post)
        else:
            g.secure_posts.append(post)

    g.public_posts = sorted(g.public_posts, key=lambda o: o.date, reverse=True)
    g.secure_posts = sorted(g.secure_posts, key=lambda o: o.date, reverse=True)

    logging.info('Load Posts Finished')


def write_posts():
    writers = []
    for writer in settings.writers:
        writers.append(import_object(writer)())

    for writer in writers:
        writer.run()


def generate(config='settings.py'):
    load_settings(config)
    load_posts(g.source_directory)
    write_posts()


def main():
    parser = argparse.ArgumentParser(prog='liquidluck')

    parser.add_argument('command', nargs='?', default='build')
    parser.add_argument('-f', '--config', default='settings.py')
    parser.add_argument('--disable-log', action='store_true',
                        dest='disable_log')

    args = parser.parse_args()
    if args.disable_log:
        enable_pretty_logging('warn')
    else:
        enable_pretty_logging()

    if args.command == 'build':
        generate(args.config)


if __name__ == '__main__':
    main()
