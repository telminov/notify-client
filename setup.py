# coding: utf-8
# python setup.py sdist register bdist_egg upload
from setuptools import setup, find_packages

setup(
    name='notify-client',
    version='0.0.3',
    description='Soft Way company notify service client.',
    author='Telminov Sergey',
    author_email='sergey@telminov.ru',
    url='https://github.com/telminov/notify-client',
    include_package_data=True,
    packages=find_packages(),
    license='The MIT License',
    install_requires=[
        'requests',
    ],
)
