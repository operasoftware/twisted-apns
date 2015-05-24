#!/bin/bash

echo -n "Version: "
read version

git tag $version
git push --tags origin master
python setup.py sdist upload -r pypi
