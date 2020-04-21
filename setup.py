from setuptools import find_packages, setup

def readme():
	with open('README.md') as f:
		README = f.read()
	return README

setup(
    name='WrfPyApp',
    version='1.1.1',
    packages=['WrfPyApp'],
    url='https://github.com/onurhdogan/WrfPyApp',
    license='MIT',
    install_requires=[
        'wrf-python==1.3.2',
        'netCDF4==1.5.3',
        'matplotlib==3.1.3'
        ],
    author='Onur Hakan Dogan',
    author_email='ohdogan@mgm.gov.tr',
    description='Crude API for the WRFPyApp',
)
