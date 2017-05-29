from setuptools import setup


setup(
    name='fudge',
    packages=['fudge'],
    entry_points={
        'console_scripts': ['fudge=fudge.cli:cli'],
    }
)
