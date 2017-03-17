from setuptools import setup, find_packages

setup(
    name = 'django_verifications',
    version = '0.0.2',
    description = 'Lightweight coding interface to manually review and freeze various model attributes using simple metadata toggles',
    long_description = 'http://labs.pewresearch.tech/docs/libs/django_verifications',
    url = 'https://github.com/pewresearch/django_verifications',
    author = 'Patrick van Kessel, Pew Research Center',
    author_email = 'pvankessel@pewresearch.tech',
    install_requires = [
        'django',
        'pewtils',
        'pandas'
    ],
    packages = find_packages(exclude = ['contrib', 'docs', 'tests']),
    include_package_data=True,
    classifiers = [
# https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 1 - Planning',
#        'Development Status :: 2 - Pre-Alpha',
#        'Development Status :: 3 - Alpha',
#        'Development Status :: 4 - Beta',
#        'Development Status :: 5 - Production/Stable',
#        'Development Status :: 6 - Mature',
#        'Development Status :: 7 - Inactive'
        'Intended Audience :: Science/Research',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7'
    ],
    keywords = 'pew pew pew',
    license = 'MIT'
)
