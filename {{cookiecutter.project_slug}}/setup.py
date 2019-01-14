try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup

config = {
    'description': '{{cookiecutter.project_short_description}}',
    'author': 'Neil Seward',
    'author_email': 'sealneaward@gmail.com',
    'version': '0.0.1',
    'packages': find_packages(),
    'name': '{{cookiecutter.bot_name}}_bot'
}

setup(**config)
