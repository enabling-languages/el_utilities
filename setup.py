from setuptools import setup

setup(
    name='el_utilities',
    version='0.1.0',
    description='Utilities used in EL apps and services",
    url='https://github.com/enabling-languages/el_utilities/',
    author='Andrew Cunningham',
    author_email='',
    license='MIT',
    packages=['el_utilities'],
    install_requires=[
        'pyicu',
        'regex',
        'unicodedataplus'
    ],
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Software Development :: Internationalization',
        'Topic :: Software Development :: Localization',
        'Topic :: Text Processing :: Linguistic',
        'Topic :: Utilities'
    ],
)
