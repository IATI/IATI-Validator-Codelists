IATI Validator Codelists
^^^^^^^^^^^^^^

Introduction
------------

This repository contains the scripts to transform the codelists for the IATI Validator.

The Codelists
=============

The source codelists can be found in the `IATI-Codelists/xml/` directory. 

Codelist Mapping Output
================

`mapping.xml <https://github.com/IATI/IATI-Codelists/blob/version-2.03/mapping.xml>`__ relates codelists to an XML path in the standard. This should make it easier for users to work out which codelists go with which element and vice versa.

This repository adds to the mapping the Codelist validation rule information used by the `IATI Validator <https://github.com/IATI/js-validator-api>`__.

It's structured as a list of `mapping` elements, which each have a `path` element that describes the relevant attribute, and a `codelist@ref` attribute which is the same ref as used in the codelist filenames. An optional `condition` element is an xpath expression which limits the scope of the given codelist - e.g. it only applies if a certain vocabulary is being used. A sample of the XML is as follows:

.. code-block:: xml

    <mappings>
        <mapping>
            <path>//iati-activity/@default-currency</path>
            <codelist ref="Currency" />
            <validation-rules>
                <validation-rule>
                    <priority>9.3</priority>
                    <severity>error</severity>
                    <category>financial</category>
                    <id>9.3.1</id>
                    <message>The default currency code is invalid.</message>
                </validation-rule>
            </validation-rules>
        </mapping>
        <mapping>
            <path>//iati-activity/recipient-region/@code</path>
            <codelist ref="Region"/>
            <condition>@vocabulary = '1' or not(@vocabulary)</condition>
            <validation-rules>
                <validation-rule>
                    <priority>9.51</priority>
                    <severity>error</severity>
                    <category>geo</category>
                    <id>9.51.1</id>
                    <message>The recipient region code is invalid.</message>
                </validation-rule>
            </validation-rules>
        </mapping>
        ...
    </mappings>


Codelist Rules
================

`codelist_rules.json <https://github.com/IATI/IATI-Validator-Codelists/blob/version-2.03/codelist_rules.json>`__ is the format of Codelist validation rules used by the `IATI Validator <https://github.com/IATI/js-validator-api>`__.

It combines information from `mapping.xml` and the different available Codelists. 

``gen.sh`` (which eventually calls ``mappings_to_codelist_rules.py``) can be used to generate ``codelist_rules.json``. 

Note running ``mappings_to_codelist_rules.py`` alone will not work as you need to pull in the NonEmbedded codelists repo, which is done in ``gen.sh``.

GitHub Actions workflows
=========================

``.github/workflows/main.yml`` does a few things when new code is pushed to  version-2.0X branches. 

* Runs xmllint and flake8 linting on the codelists in ``xml/``
* Pushes ``codelist_rules.json`` to the Redis cache used by the IATI Validator
* Triggers a workflow to update the .csv Validator rules in `Validator Rule Tracker <https://github.com/IATI/validator-rule-tracker>`__

Information for developers
==========================

This tool supports Python 3.x. To use this script, we recommend the use of a virtual environment::

    python3 -m venv pyenv
    source pyenv/bin/activate
    pip install -r requirements.txt
