IATI Validator Codelists
^^^^^^^^^^^^^^^^^^^^^^^^

Introduction
------------

This repository contains the scripts to transform the codelists for the IATI Validator.

Versions
========

There is one branch per active version of the IATI Standard:

- ``version-2.01``
- ``version-2.02``
- ``version-2.03``

The Codelists
=============

The source codelists can be found in the `IATI-Codelists/xml/` directory. 

Codelist Mapping Output
=======================

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

Update Process
==============

* Can happen through either a manual update to this repo through a Pull Request, or an automated update from IATI-Codelists or IATI-Codelists-NonEmbedded
* An automated update from IATI-Codelists or IATI-Codelists-NonEmbedded will create PRs (one per affected version) in this repo for changes and assign @IATI/devs group for review.
* Any PRs with changes to `codelist_rules.json` should be reviewed/merged, which then pushes the codelist file to our Dev/Prod Redis cache
* Once that occurs the Validator Azure Functions must be restarted to pickup the new `codelist_rules.json` file from the Redis cache
* You can confirm the update works by validating a file and comparing the `"codelistCommitSha"` key in the response to the commit sha  of the `codelist_rules.json` file in the repo for the specific version 

GitHub Actions workflows
=========================

``.github/workflows/dispatch-CI.yaml``

Trigger: 

* GitHub Dispatch API Call from `IATI-Codelists <https://github.com/IATI/IATI-Codelists>`__ or `IATI-Codelists-NonEmbedded <https://github.com/IATI/IATI-Codelists-NonEmbedded>`__
* Manual workflow dispatch from the GitHub Actions UI

Actions:

* Sets up the python environment, builds `codelist_rules.json`
* If there are changes, creates a PR for manual review and merging to prevent auto-updates to the validator codelists breaking it.


``.github/workflows/PR-CI.yaml``

Trigger: 

* Pull Request

Actions:

* Sets up the python environment, builds `codelist_rules.json`
* Diffs with existing `codelist_rules.json`, if there are differences it fails. 

Why: If you are making updates to `codelist_rules.json` you must include them in a PR

``.github/workflows/push-CI.yaml``

Trigger: 
* Push to the branch (e.g. when PR merged)

Actions:
* Triggers a workflow to update the .csv Validator rules in `Validator Rule Tracker <https://github.com/IATI/validator-rule-tracker>`__ which utilises the `rule_mapping.xml` file. 
* Pushes ``codelist_rules.json`` to the Redis caches used by the IATI Validator

Information for developers
==========================

This tool supports Python 3.x. To use this script, we recommend the use of a virtual environment::

    python3 -m venv pyenv
    source pyenv/bin/activate
    pip install -r requirements.txt
