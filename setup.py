# -*- coding: UTF-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


from setuptools import find_packages


def get_packages():
    find_packages(exclude=['docs', 'tests']),
    return find_packages()


def get_version():
    version = dict()

    with open("gscpy/__version__.py") as fp:
        exec (fp.read(), version)

    return version['__version__']


setup(name='gscpy',

      version=get_version(),

      description='Sentinel-1 SAR space-time cube with radar pre-processing in GRASS',

      packages=get_packages(),

      author="Ismail Baris, Nils von Norsinski",
      maintainer='Ismail Baris',

      # ~ license='APACHE 2',

      url='https://github.com/ibaris/gscpy',

      long_description='Sentinel-1 SAR space-time cube with radar pre-processing in GRASS',
      # install_requires=install_requires,

      keywords=["radar", "remote-sensing", "optics", "integration",
                "microwave", "estimation", "physics", "radiative transfer"],

      # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          'Intended Audience :: Science/Research',
          'Topic :: Scientific/Engineering :: Atmospheric Science',

          # Pick your license as you wish (should match "license" above)
          'License :: OSI Approved :: MIT License',

          'Programming Language :: Python :: 2.7',
          'Operating System :: Microsoft',

      ],
      # package_data={"": ["*.txt"]},
      include_package_data=True,
      install_requires=['numpy', 'scipy'],
      setup_requires=[
          'pytest-runner',
      ],
      tests_require=[
          'pytest',
      ],
      )
