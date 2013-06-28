import ez_setup
ez_setup.use_setuptools()

import setuptools

setuptools.setup(
    name="dale-beets-plugins",
    version="0.1",
    packages=setuptools.find_packages(),
    install_requires=['beets>=1.2.2,==dev'],
)
