#!/bin/bash

if [ "$TRAVIS_BRANCH" == "master" ]; then
  bash <(curl --insecure -Ls https://coverage.codacy.com/get.sh) report -r coverage.xml
fi
