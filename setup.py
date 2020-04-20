from setuptools import find_packages, setup

setup(
    name='WrfPyApp',
    version='1.0',
    packages=find_packages(),
    packages=['WrfPyApp'],
    url='https://github.com/onurhdogan/WrfPyApp',
    license='MIT',
    install_requires=[
        'tkinter',
        'wrf-python',
        'netCDF4',
        'matplotlib'
        ],
    author='Onur Hakan Dogan',
    author_email='ohdogan@mgm.gov.tr',
    description='Crude API for the WRFPyApp',
)
