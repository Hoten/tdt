from setuptools import setup

setup(
    name = 'tdt',
    version = '0.1.0',
    author='Connor Clark',
    description='Generate Tech Debt reports',
    packages = ['tdt'],
    entry_points = {
        'console_scripts': [
            'tdt = tdt.__main__:main'
        ]
    })
