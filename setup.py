'''/*---------------------------------------------------------------------------------------------
 *  Copyright (c) VituTech. All rights reserved.
 *  Licensed under the Apache License 2.0. See License.txt in the project root for license information.
 *--------------------------------------------------------------------------------------------*/
 '''
 
"""A setuptools based setup module for h5json.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""
from setuptools import setup
from os import path
import os

here = path.abspath(path.dirname(__file__))
root_dir = 'vitu'
py_modules = set()
py_packages = set()

for root, dirs, files in os.walk(root_dir):
    for f in files:
        if f.endswith('.py'):
            if root == root_dir:
                py_modules.add(root + '.' + f.split('.')[0])

            if root != root_dir:
                py_packages.add(root.replace(os.path.sep, '.'))
py_packages.add('vitudata')
py_packages.add('vitudata.apis')            
print(py_modules)
print(py_packages)
setup(
    name='vitu',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version='2.0.0',

    description='VITU/Halo - backtest framework',
    long_description='VITU/Halo - backtest framework',

    # The project's main homepage.
    url='http://vitu.ai',

    # Author details
    author='VituTech',
    author_email='service@vitutech.com',

    # Choose your license
    # license='BSD',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 5 - Production/Stable',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish (should match "license" above)
        # 'License :: OSI Approved :: BSD License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],

    python_requires='>=3.0, <4',
    # What does your project relate to?
    keywords='vitu halo backtest',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    #packages=find_packages(exclude=['docs', 'test*']),
    packages=list(py_packages),

    # Alternatively, if you want to distribute just a my_module.py, uncomment
    # this:
    py_modules=list(py_modules),

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    setup_requires=['pkgconfig', 'six'],
    zip_safe=False,

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    extras_require={
        'dev': ['check-manifest'],
        'test': ['coverage'],
    },

    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    package_data={
        'vitu': ['wqy-microhei.ttc']
    },

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages. See:
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files # noqa
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    data_files=[('vitu', ['vitu/wqy-microhei.ttc'])],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    
)
