import os
from setuptools import find_packages, setup

ROOT_DIR = os.path.dirname(__file__)
SOURCE_DIR = os.path.join(ROOT_DIR)

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

def get_requirements(requirements_file):
    with open(requirements_file) as f:
        required = [line.split('#')[0] for line in f.read().splitlines()]
    return required

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='juntagrico-custom-sub',
    version='0.dev.1',
    packages=find_packages(),
    include_package_data=True,
    license='LPGLv3',  # example license
    description='juntagrico-custom-sub',
    long_description=README,
    url='http://juntagrico.org',
    author='juntagrico',
    author_email='info@juntagrico.org',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.0',  # replace "X.Y" as appropriate
        'Intended Audience :: Developers',
        'License :: OSI Approved :: LPGLv3',  # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        # Replace these appropriately if you are stuck on Python 2.
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires=get_requirements(os.path.join(ROOT_DIR, 'requirements.txt')),
)
