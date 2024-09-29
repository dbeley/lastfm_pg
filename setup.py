import setuptools
import lastfm_pg

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="lastfm_pg",
    version=lastfm_pg.__version__,
    author="dbeley",
    author_email="dbeley@protonmail.com",
    description="Generate playlists from the top tracks listened by a lastfm user.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dbeley/lastmf_pg",
    packages=setuptools.find_packages(),
    include_package_data=True,
    entry_points={"console_scripts": ["lastfm_pg=lastfm_pg.__main__:main"]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: POSIX :: Linux",
    ],
    install_requires=["pylast", "Mastodon.py"],
)
