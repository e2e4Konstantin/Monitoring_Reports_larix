# pip install -e . (note the dot, it stands for "current directory")
from setuptools import setup, find_packages

setup(
    name="MonitoringReports_larix",
    version="0.1.0",
    author="Konstantin Kazak",
    author_email="e2e4suchok@gmail.com",
    description="Сreates a report on the data of the monitoring department",
    #
    packages=find_packages(),
)

# https://stackoverflow.com/questions/71080546/what-is-the-preferred-way-to-develop-a-python-package-without-using-setup-py
# https://packaging.python.org/en/latest/guides/modernize-setup-py-project/
# https://pip.pypa.io/en/latest/reference/build-system/pyproject-toml/
