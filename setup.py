from setuptools import setup

# https://blog.whtsky.me/tech/2021/dont-forget-py.typed-for-your-typed-python-package/
# https://peps.python.org/pep-0561/#packaging-type-information
# PEP561 has a spec where a py.typed folder will tell a build tool to package type
# hints when building. It's as simple as adding an empty file named "py.typed" into the
# package directory
setup(package_data={"xlib_commonpy": ["py.typed"]})
