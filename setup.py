from setuptools import setup


setup(
    name='fudge',
    packages=['fudge'],
    install_requires=[
        'requests',
        'sortedcontainers',
    ],
    entry_points={
        'console_scripts': ['fudge=fudge.cli:cli'],
    },
)
