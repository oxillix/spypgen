import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="spygen-n-ivanov",
    version="0.1",
    author="Nikita Ivanov",
    author_email="nikita.vl.ivanov@protonmail.com",
    description="Generates Spotify playlists using data aggregated from Spotify and 1001Tracklists",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/n-ivanov/spypgen",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.5",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
    ],
)
