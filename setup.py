
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="hack12306",
    version="0.0.4",
    author="Meng yangyang",
    author_email="mengyy_linux@163.com",
    description="Hack 12306",
    license='MIT',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hack12306/hack12306",
    packages=setuptools.find_packages(),
    install_requires=["requests>=2.12.4", "BeautifulSoup>=3.2.1"],
    classifiers=[
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
