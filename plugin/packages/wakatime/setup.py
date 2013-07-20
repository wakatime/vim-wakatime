from setuptools import setup

from wakatime.__init__ import __version__ as VERSION


packages = [
    'wakatime',
]

setup(
    name='wakatime',
    version=VERSION,
    license='BSD 3 Clause',
    description=' '.join([
        'Action event appender for Wakati.Me, a time',
        'tracking api for text editors.',
    ]),
    long_description=open('README.rst').read(),
    author='Alan Hamlett',
    author_email='alan.hamlett@gmail.com',
    url='https://github.com/wakatime/wakatime',
    packages=packages,
    package_dir={'wakatime': 'wakatime'},
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    entry_points={
        'console_scripts': ['wakatime = wakatime.__init__:main'],
    },
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Topic :: Text Editors',
    ),
)
