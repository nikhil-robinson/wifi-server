from setuptools import setup, find_packages
import os

# get the absolute path of the current directory
HERE = os.path.abspath(os.path.dirname(__file__))

# read the contents of the README file
with open(os.path.join(HERE, "README.md"), encoding="utf-8") as f:
    README = f.read()

# define the package requirements
requirements = [
    'qrcode',
    'Pillow',
    'psutil',
    'tk',
]

# setup the package
setup(
    name="wifi-hotspot-creator",
    version="1.0",
    description="Create a Wi-Fi hotspot with a GUI interface",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/nikhil-robinson/wifi-server",
    author="Nikhil Robinson",
    author_email="nikhilrobinson2000@gmail.com",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "wifi-hotspot-creator=yourpackage.app:main",
        ],
    },
    # define the permissions to set on the script
    data_files=[('share/applications', ['/home/nikhil/Desktop/Nikhil/wifi-server/wifi-hotspot-creator.desktop'])],
    options={
        "install": {
            "optimize": 1,
            "force": True,
            "root": "/",
            "prefix": "/usr",
            "record": "/tmp/record.txt",
        },
    },
)