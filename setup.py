from setuptools import setup


setup(
    name='fudge',
    packages=['fudge'],
    install_requires=[
        'requests',
    ],
    entry_points={
        'console_scripts': ['fudge=fudge.cli:cli'],
    }
)
