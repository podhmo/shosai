import os

from setuptools import setup, find_packages
here = os.path.abspath(os.path.dirname(__file__))
try:
    with open(os.path.join(here, "README.rst")) as f:
        README = f.read()
    with open(os.path.join(here, "CHANGES.txt")) as f:
        CHANGES = f.read()
except IOError:
    README = CHANGES = ""

install_requires = [
    "requests",
    "requests_oauthlib",  # for hatena
    "xmltodict",  # for hatena
    "mistune",
    "mypy_extensions",
]

docs_extras = []

tests_require = []

testing_extras = tests_require + []

setup(
    name="shosai",
    version="0.0.3",
    description="-",
    long_description=README + "\n\n" + CHANGES,
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
    keywords=["markdown", "docbase", "hatena"],
    author="podhmo",
    author_email="ababjam61+github@gmail.com",
    url="https://github.com/podhmo/shosai",
    packages=find_packages(exclude=["shosai.tests"]),
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    extras_require={
        "testing": testing_extras,
        "docs": docs_extras,
    },
    tests_require=tests_require,
    test_suite="shosai.tests",
    entry_points="""
      [console_scripts]
      shosai = shosai.commands.shosai:main
      shosai-internal = shosai.commands.shosai_internal:main
"""
)
