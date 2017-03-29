import os
from setuptools import setup, find_packages
from django_verifications import __version__

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

with open('requirements.txt') as reqs:
    install_requires = [
        line for line in reqs.read().split('\n') if line and not line.startswith(('--', 'git+ssh'))
    ]
    dependency_links = [
        line for line in reqs.read().split('\n') if line and line.startswith(('--', 'git+ssh'))
    ]

setup(
    name = 'django_verifications',
    version = __version__,
    description = 'Lightweight coding interface to manually review and freeze various model attributes using simple metadata toggles',
    long_description = README, # 'http://labs.pewresearch.tech/docs/libs/django_verifications',
    url = 'https://github.com/pewresearch/django_verifications',
    author = 'Patrick van Kessel, Pew Research Center',
    author_email = 'pvankessel@pewresearch.tech',
    install_requires = install_requires,
    dependency_links = dependency_links,
    packages = find_packages(exclude = ['contrib', 'docs', 'tests']),
    include_package_data=True,
    classifiers = [
        'Environment :: Web Environment',
        'Framework :: Django',
# https://pypi.python.org/pypi?%3Aaction=list_classifiers
#        'Development Status :: 1 - Planning',
        'Development Status :: 2 - Pre-Alpha',
#        'Development Status :: 3 - Alpha',
#        'Development Status :: 4 - Beta',
#        'Development Status :: 5 - Production/Stable',
#        'Development Status :: 6 - Mature',
#        'Development Status :: 7 - Inactive'
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7'
    ],
    keywords = 'pew pew pew',
    license = 'MIT'
)
