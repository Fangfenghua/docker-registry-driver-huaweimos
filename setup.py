#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    import setuptools
except ImportError:
    import distutils.core as setuptools


__author__ = 'TEC DEV TEAM'
__copyright__ = 'Copyright 2015'
__credits__ = []

__version__ = '0.1.3'
__maintainer__ = 'TEC DEV TEAM'
__email__ = 'fangfenghua@huawei.com'

__title__ = 'docker-registry-driver-huaweimos'
__build__ = 0x000000

__url__ = 'https://github.com/kerwin/docker-registry-driver-huaweimos'
__description__ = 'Docker registry huawei mos driver'

setuptools.setup(
    name=__title__,
    version=__version__,
    author=__author__,
    author_email=__email__,
    maintainer=__maintainer__,
    maintainer_email=__email__,
    url=__url__,
    description=__description__,
    classifiers=['Development Status :: 4 - Beta',
                 'Intended Audience :: Developers',
                 'Programming Language :: Python',
                 'Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: Implementation :: CPython',
                 'Operating System :: OS Independent',
                 'Topic :: Utilities'],
    platforms=['Independent'],
    namespace_packages=['docker_registry',
                        'docker_registry.drivers',
                        'docker_registry.contrib'],
    packages=['docker_registry',
              'docker_registry.drivers',
              'docker_registry.contrib',
              'docker_registry.contrib.hws-python-sdk.src.com'],
    package_data = {'docker_registry': ['../config/*']},
    install_requires=[
        "docker-registry-core>=2,<3"
    ],
    zip_safe=True,
    tests_require=[
        "nose==1.3.3"
    ],
    test_suite='nose.collector'
)

