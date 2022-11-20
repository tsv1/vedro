from setuptools import find_packages, setup


def find_required():
    with open("requirements.txt") as f:
        return f.read().splitlines()


def find_dev_required():
    with open("requirements-dev.txt") as f:
        return f.read().splitlines()


setup(
    name="vedro",
    version="1.7.2",
    description="Pragmatic BDD Framework",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Nikita Tsvetkov",
    author_email="nikitanovosibirsk@yandex.com",
    python_requires=">=3.7",
    url="https://github.com/nikitanovosibirsk/vedro",
    project_urls={
        "Docs": "https://vedro.io/",
        "GitHub": "https://github.com/nikitanovosibirsk/vedro",
    },
    license="Apache-2.0",
    packages=find_packages(exclude=["tests", "tests.*"]),
    package_data={"vedro": ["py.typed"]},
    entry_points={
        "console_scripts": ["vedro = vedro:run"],
    },
    install_requires=find_required(),
    tests_require=find_dev_required(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development",
        "Typing :: Typed",
    ],
)
