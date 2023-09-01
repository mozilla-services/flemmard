Flemmard
========

.. image:: images/flemmard.png
   :align: right



**Flemmard** is a script you can use to drive Jenkins from the command line.


The script let you:

- build jobs with specific tags
- download artifacts
- create new jobs using a job template
- list jobs and their status


Usage
-----

Flemmard provides a command-line script called ... **flemmard** that comes
with actions:

- **list** -- Lists all jobs.
- **status** -- Gives a job status
- **build** -- Build a job.
- **create** -- Create a new Job
- **artifacts** -- Lists the artifacts.

For every action, you can specify the Jenkins root URL with *--url*, or
add a *.flemmardrc* file into your home directory to set up a default value::

    [flemmard]
    url = http://jenkins.example.com


Using *--url* explicitely will override any value found in *.flemmardrc*.




Useful links
------------


- Repository : https://github.com/mozilla-services/flemmard


