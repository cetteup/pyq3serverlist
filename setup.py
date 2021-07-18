from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='pyq3serverlist',
    version='0.1.6',
    description='Simple Python library for querying Quake 3 based principal servers and their game servers',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/cetteup/pyq3serverlist',
    project_urls={
        'Bug Tracker': 'https://github.com/cetteup/pyq3serverlist/issues',
    },
    author='cetteup',
    author_email='me@cetteup.com',
    license='MIT',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3'
    ],
    packages=['pyq3serverlist'],
    python_requires='>=3.6'
)
