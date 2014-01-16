
History
-------


1.5.1 (2014-01-15)
++++++++++++++++++

- upgrade external wakatime package to v0.5.3
- bug fix for unicode in Python3


1.5.0 (2013-12-16)
++++++++++++++++++

- upgrade external wakatime package to v0.5.1
- fix MAXREPEAT bug in Python2.7 by not using python in VimL


1.4.0 (2013-12-13)
++++++++++++++++++

- upgrade external wakatime package to v0.5.0
- convert ~/.wakatime.conf to ~/.wakatime.cfg and use configparser format


1.3.1 (2013-12-02)
++++++++++++++++++

- support non-English characters in file names


1.3.0 (2013-11-28)
++++++++++++++++++

- increase frequency of pings to api from every 5 mins to every 2 mins
- upgrade external wakatime package to v0.4.10
- support .wakatime-project files for custom project names


1.2.3 (2013-10-27)
++++++++++++++++++

- upgrade external wakatime package to v0.4.9
- new config file option to ignore and prevent logging files based on regex


1.2.2 (2013-10-13)
++++++++++++++++++

- upgrade external wakatime package to v0.4.8
- prevent popup windows when detecting Git project on Windows platform


1.2.1 (2013-09-30)
++++++++++++++++++

- upgrade external wakatime package to v0.4.7
- send local olson timezone string in api requests


1.2.0 (2013-09-22)
++++++++++++++++++

- upgrade external wakatime package to v0.4.6
- logging total lines in current file and language used


1.1.5 (2013-09-07)
++++++++++++++++++

- upgrade external wakatime package to v0.4.5
- fix relative import error by adding packages directory to sys path


1.1.4 (2013-09-06)
++++++++++++++++++

- upgrade external wakatime package to v0.4.4
- use urllib2 again because of problems sending json with requests module


1.1.3 (2013-09-04)
++++++++++++++++++

- upgrade external wakatime package to v0.4.3


1.1.2 (2013-09-04)
++++++++++++++++++

- upgrade external wakatime package to v0.4.2


1.1.1 (2013-08-25)
++++++++++++++++++

- upgrade external wakatime package to v0.4.1


1.1.0 (2013-08-15)
++++++++++++++++++

- upgrade external wakatime package to v0.4.0
- detect branch from revision control


1.0.0 (2013-08-12)
++++++++++++++++++

- upgrade external wakatime package to v0.3.1
- use requests module instead of urllib2 to verify SSL certs


0.2.6 (2013-07-29)
++++++++++++++++++

- upgrade external wakatime package to v0.2.0 for python2 and python3 support


0.2.5 (2013-07-22)
++++++++++++++++++

- upgrade external wakatime package to v0.1.4
- use timeout and api pings to calculate logged time server-side instead of sending end_time


0.2.4 (2013-07-20)
++++++++++++++++++

- upgrade external wakatime package to v0.1.3
- run external wakatime script with any python version instead of forcing python2
- support for Subversion projects


0.2.3 (2013-07-16)
++++++++++++++++++

- fix bug when calculation away duration
- fixed bug where away prompt would do the opposite of user's choice
- force external wakatime script to run with python2
- many bug fixes


0.2.2 (2013-07-10)
++++++++++++++++++

- fix bug where event missed when first opening Vim with a file
- remove verbose flag to stop printing debug messages
- stop using VimL strings as floats
- only log events once every 5 minutes, except for write events
- prompt user for api key if one does not already exist
- set 5 second delay between writing last cursor event time to local file
- many bug fixes


0.2.1 (2013-07-07)
++++++++++++++++++

- move api interface code into external wakatime repository
- support for Git projects
- support changes to api schema which break backwards compatibility
- simplify user events into regular events and write events


0.1.3 (2013-07-02)
++++++++++++++++++

- move wakatime.log to $HOME folder
- support Vim's +clientserver for multiple instances of Vim
- auto create log file if it does not exist
- fixed bugs


0.1.2 (2013-06-25)
++++++++++++++++++

- Birth

