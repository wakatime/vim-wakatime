
History
-------


0.5.3 (2014-01-15)
++++++++++++++++++

- bug fix for unicode in Python3


0.5.2 (2014-01-14)
++++++++++++++++++

- minor bug fix for Subversion on non-English systems


0.5.1 (2013-12-13)
++++++++++++++++++

- second line in .wakatime-project file now sets branch name


0.5.0 (2013-12-13)
++++++++++++++++++

- Convert ~/.wakatime.conf to ~/.wakatime.cfg and use configparser format
- new [projectmap] section in cfg file for naming projects based on folders


0.4.10 (2013-11-13)
+++++++++++++++++++

- Placing .wakatime-project file in a folder will read the project's name from that file


0.4.9 (2013-10-27)
++++++++++++++++++

- New config for ignoring files from regular expressions
- Parse more options from config file (verbose, logfile, ignore)


0.4.8 (2013-10-13)
++++++++++++++++++

- Read git HEAD file to find current branch instead of running git command line


0.4.7 (2013-09-30)
++++++++++++++++++

- Sending local olson timezone string in api request


0.4.6 (2013-09-22)
++++++++++++++++++

- Sending total lines in file and language name to api


0.4.5 (2013-09-07)
++++++++++++++++++

- Fixed relative import error by adding packages directory to sys path


0.4.4 (2013-09-06)
++++++++++++++++++

- Using urllib2 again because of intermittent problems sending json with requests library


0.4.3 (2013-09-04)
++++++++++++++++++

- Encoding json as utf-8 before making request


0.4.2 (2013-09-04)
++++++++++++++++++

- Using requests package v1.2.3 from pypi


0.4.1 (2013-08-25)
++++++++++++++++++

- Fix bug causing requests library to omit POST content


0.4.0 (2013-08-15)
++++++++++++++++++

- Sending single branch instead of multiple tags


0.3.1 (2013-08-08)
++++++++++++++++++

- Using requests module instead of urllib2 to verify SSL certs


0.3.0 (2013-08-08)
++++++++++++++++++

- Allow importing directly from Python plugins


0.1.1 (2013-07-07)
++++++++++++++++++

- Refactored
- Simplified action events schema


0.0.1 (2013-07-05)
++++++++++++++++++

- Birth

