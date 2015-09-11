from setuptools import setup, find_packages

setup(
	name='njt',
	version='0.1',
	packages=find_packages(),
	entry_points={'njt':['settings = njt.settings']},
)