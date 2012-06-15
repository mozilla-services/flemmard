from setuptools import setup, find_packages

install_requires = ['python-jenkins', 'jenkinsapi']


with open("README.rst") as f:
    README = f.read()

with open("CHANGES.rst") as f:
    CHANGES = f.read()


setup(name='flemmard',
      version='0.1',
      packages=find_packages(),
      description=("Drive your Mozilla Services Jenkins projects from the "
                   "command line"),
      long_description=README + '\n' + CHANGES,
      author="Mozilla Foundation",
      author_email="services-dev@lists.mozila.org",
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      test_requires=['nose'],
      test_suite = 'nose.collector',
      entry_points="""
      [console_scripts]
      flemmard = flemmard:main
      """)
