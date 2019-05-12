from setuptools import setup

setup(
    name = 'spypgen',
    version = '1.0.0',
    packages = ['spypgen'],
    entry_points = {
        'console_scripts': [
            'spypgen = spypgen.__main__.main'
        ]
    })