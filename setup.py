#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    import setuptools
except ImportError:
    import distutils.core as setuptools


__author__ = 'TEC DEV TEAM'
__copyright__ = 'Copyright 2015'
__credits__ = []

__version__ = '0.0.1'
__maintainer__ = 'TEC DEV TEAM'
__email__ = '449171342@qq.com'
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
                        'docker_registry.drivers'],
    packages=['docker_registry',
              'docker_registry.drivers',
              'com',
              'com.hws',
              'com.hws.s3',
              'com.hws.s3.client',
              'com.hws.s3.models',
              'com.hws.s3.response',
              'com.hws.s3.utils'
             ],
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

