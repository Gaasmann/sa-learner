#!/usr/bin/env python3

from setuptools import setup

setup(name='salearner',
        version='0.1',
        description='TensorFlow POC optimizing SA scoring',
        url='https://github.com/Gaasmann/sa-learner',
        author='Nicolas Haller',
        author_email='nicolas@boiteameuh.org',
        license='MIT',
        packages=['salearner'],
        install_requires=['numpy'],
        include_package_data=True,
        zip_safe=False)
