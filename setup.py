from setuptools import setup

install_requires = [
    'python-dateutil==2.5.3',
    'PyGithub==1.26.0',
]

setup(
    name='lgtm',
    version='0.0.1',
    packages=['lgtm'],
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
