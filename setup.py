""" Setup configuration fo pypi

"""
from setuptools import setup
setup(
    name='mercedesmejsonpy',
    version='0.1.1',
    packages=['mercedesmejsonpy'],
    include_package_data=True,
    python_requires='>=3',
    license='WTFPL',
    description='A library to work with Mercedes ME API.',
    long_description='A library to work with Mercedes ME car API.',
    author='Rene Nulsch',
    author_email='github.mercedesmejsonpy@nulsch.de',
    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet',
    ],
    install_requires=[
        'lxml>=4.1.0',
        'requests>=2.18.4'
    ]
)
