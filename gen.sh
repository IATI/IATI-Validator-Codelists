#!/bin/bash

cd IATI-Codelists
./gen.sh
cd ..

python mappings_to_codelist_rules.py
