#!/usr/bin/env python3

from setuptools import setup

setup(name='salearner',
        version='0.1',
        description='TensorFlow POC optimizing SA scoring',
        url='https://github.com/Gaasmann/sa-learner',
        author='Nicolas Haller',
        author_email='nicolas@boiteameuh.org',
        license='MIT',
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Information Technology',
            'Intended Audience :: System Administrators',
            'License :: OSI Approved :: MIT License',
            'Natural Language :: English',
            'Topic :: Communications :: Email',
            'Scientific/Engineering :: Artificial Intelligence'],
        packages=['salearner'],
        install_requires=['numpy'],
        include_package_data=True,
        zip_safe=False)
