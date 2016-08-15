from setuptools import setup, find_packages

install_requires = [
    'python-dateutil>=2.4.2,<3.0.0',
    'PyGithub>=1.26.0,<2.0.0',
]

setup(
    name='lgtm',
    version='0.0.12',
    packages=find_packages(exclude=['tests', 'lgtm/tests']),
    install_requires=install_requires,
    include_package_data=True,
    author='Chase Seibert',
    author_email='cseibert@nerdwallet.com',
    license='Other/Proprietary License',
    description='A pull request approval system using GitHub protected branches and OWNERS files.',
    long_description='',
    url='https://github.com/nerdwallet/github-lgtm',
    entry_points={
        'console_scripts': ['lgtm=lgtm.console:main'],
    },
)
