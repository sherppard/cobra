#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    cobra
    ~~~~~

    Implements cobra main

    :author:    Feei <wufeifei#wufeifei.com>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2016 Feei. All rights reserved
"""
import os
import logging.config
from app import web, manager
from utils import config


def main():
    logs_directory = config.Config('cobra', 'logs_directory').value
    logs_directory = os.path.join(config.Config().project_directory, logs_directory)
    if os.path.isdir(logs_directory) is not True:
        os.mkdir(logs_directory)
    filename = os.path.join(logs_directory, 'cobra.log')
    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': True,
        'formatters': {
            'verbose': {
                'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
                'datefmt': "%Y-%m-%d %H:%M:%S"
            },
            'simple': {
                'format': '%(levelname)s %(message)s'
            },
        },
        'handlers': {
            'file': {
                'level': 'DEBUG',
                'class': 'cloghandler.ConcurrentRotatingFileHandler',
                'maxBytes': 1024 * 1024 * 10,
                'backupCount': 50,
                'delay': True,
                'filename': filename,
                'formatter': 'verbose'
            }
        },
        'loggers': {
            '': {
                'handlers': ['file'],
                'level': 'INFO',
            },
        }
    })

    debug = config.Config('cobra', 'debug').value
    web.debug = bool(debug)
    manager.run()


if __name__ == '__main__':
    main()
