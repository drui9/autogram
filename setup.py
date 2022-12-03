from setuptools import setup, find_packages


def dependencies():
    with open('requirements.txt', 'r') as rfile:
        depends = [i.strip() for i in rfile.readlines()]
    return depends


def readme():
    with open('README.md', 'r') as md:
        return md.read()


setup(
    version='1.1',
    name='autogram',
    author='sp3rtah',
    packages=find_packages(),
    long_description=readme(),
    install_requires=dependencies(),
    description='Telegram bot with inbuilt batteries!'
)
