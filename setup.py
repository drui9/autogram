from setuptools import setup, find_packages
from collections import namedtuple

Dependencies = namedtuple('Dependencies',['dev','release'])


def dependencies():
    release, dev = list(), list()
    release_marker = '[packages]'
    with open('Pipfile', 'r') as dfile:
        lines = dfile.read().split(release_marker)[1].split('\n')
        stop_idx = lines.index('', 1)
        for i in range(1, stop_idx):
            dep = lines[i]
            if d := dep.strip():
                release.append(d.split('=')[0])
        stop_idx += 1  # for blank line after
        for i in range(stop_idx + 1, lines.index('', stop_idx + 1)):
            dep = lines[i]
            if d := dep.strip():
                dev.append(d.split('=')[0])
    return Dependencies(dev=dev, release= release)


def readme():
    with open('README.md', 'r') as md:
        return md.read()


setup(
    name='autogram',
    version='1.2',
    author='sp3rtah',
    description='Telegram bot with batteries included!',
    long_description=readme(),
    packages=find_packages(),
    install_requires=dependencies().release
)
