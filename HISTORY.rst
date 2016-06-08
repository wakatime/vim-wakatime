
History
-------


4.0.12 (2016-06-08)
++++++++++++++++++

- Upgrade wakatime-cli to master version to fix bug in urllib3 package causing
  unhandled retry exceptions.
- Prevent tracking git branch with detached head.
- Support for SOCKS proxies.


4.0.11 (2016-05-16)
++++++++++++++++++

- Upgrade wakatime-cli to v6.0.2.
- Prevent popup on Mac when xcode-tools is not installed.


4.0.10 (2016-04-19)
++++++++++++++++++

- Pass syntax of current file to wakatime-cli.
- Upgrade wakatime-cli to v5.0.1.
- Support passing an alternate language to cli to be used when a language can
  not be guessed from the code file.


4.0.9 (2016-04-18)
++++++++++++++++++

- Upgrade wakatime-cli to v5.0.0.
- Support regex patterns in projectmap config section for renaming projects.
- Upgrade pytz to v2016.3.
- Upgrade tzlocal to v1.2.2.


4.0.8 (2016-03-06)
++++++++++++++++++

- upgrade wakatime-cli to v4.1.13
- encode TimeZone as utf-8 before adding to headers
- encode X-Machine-Name as utf-8 before adding to headers


4.0.7 (2016-01-11)
++++++++++++++++++

- upgrade wakatime cli to v4.1.10
- improve C# dependency detection
- correctly log exception tracebacks
- log all unknown exceptions to wakatime.log file
- disable urllib3 SSL warning from every request
- detect dependencies from golang files
- use api.wakatime.com for sending heartbeats
- accept 201 or 202 response codes as success from api
- upgrade requests package to v2.9.1


4.0.6 (2015-12-01)
++++++++++++++++++

- upgrade wakatime cli to v4.1.8
- default request timeout of 30 seconds
- new --timeout command line argument to change request timeout in seconds
- fix bug in guess_language function
- improve dependency detection


4.0.5 (2015-09-07)
++++++++++++++++++

- upgrade wakatime cli to v4.1.6
- fix bug in offline caching which prevented heartbeats from being cleaned up
- fix local session caching
- new --entity and --entitytype command line arguments
- fix entry point for pypi distribution
- allow passing command line arguments using sys.argv


4.0.4 (2015-08-25)
++++++++++++++++++

- upgrade wakatime cli to v4.1.1
- send hostname in X-Machine-Name header
- catch exceptions from pygments.modeline.get_filetype_from_buffer
- upgrade requests package to v2.7.0
- handle non-ASCII characters in import path on Windows, won't fix for Python2
- upgrade argparse to v1.3.0
- move language translations to api server
- move extension rules to api server
- detect correct header file language based on presence of .cpp or .c files named the same as the .h file


4.0.3 (2015-06-23)
++++++++++++++++++

- fix offline logging
- limit language detection to known file extensions, unless file contents has a vim modeline
- upgrade wakatime cli to v4.0.16


4.0.2 (2015-06-11)
++++++++++++++++++

- upgrade wakatime cli to v4.0.15
- guess language using multiple methods, then use most accurate guess
- use entity and type for new heartbeats api resource schema


4.0.1 (2015-05-31)
++++++++++++++++++

- upgrade wakatime cli to v4.0.14
- make sure config file has api_key
- only display setup complete message first time setting up cfg file
- don't log time towards git temporary files
- prevent slowness in quickfix window to fix #24
- reuse SSL connection across multiple processes for improved performance
- correctly display caller and lineno in log file when debug is true
- project passed with --project argument will always be used
- new --alternate-project argument
- fix bug with auto detecting project name
- correctly log message from py.warnings module
- handle plugin_directory containing spaces


4.0.0 (2015-05-01)
++++++++++++++++++

- upgrade wakatime cli to v4.0.8
- check for api_key in config file instead of just checking if file exists


3.0.9 (2015-04-02)
++++++++++++++++++

- upgrade wakatime cli to v4.0.7
- update requests package to v2.0.6
- update simplejson to v3.6.5
- capture warnings in log file


3.0.8 (2015-03-09)
++++++++++++++++++

- upgrade wakatime cli to v4.0.4
- new options for excluding and including directories


3.0.7 (2015-02-12)
++++++++++++++++++

- upgrade external wakatime-cli to v4.0.0
- use requests library instead of urllib2, so api SSL cert is verified
- new proxy config file item for https proxy support


3.0.6 (2015-01-19)
++++++++++++++++++

- prompt for api key only after first buffer window opened
- include vim version number in plugin user agent string


3.0.5 (2015-01-13)
++++++++++++++++++

- upgrade external wakatime package to v3.0.5
- ignore errors from malformed markup (too many closing tags)


3.0.4 (2015-01-06)
++++++++++++++++++

- upgrade external wakatime package to v3.0.4
- remove unused dependency, which is missing in some python environments


3.0.3 (2014-12-25)
++++++++++++++++++

- upgrade external wakatime package to v3.0.3
- detect JavaScript frameworks from script tags in Html template files


3.0.2 (2014-12-25)
++++++++++++++++++

- upgrade external wakatime package to v3.0.2
- detect frameworks from JavaScript and JSON files


3.0.1 (2014-12-23)
++++++++++++++++++

- upgrade external wakatime package to v3.0.1
- handle unknown language when parsing dependencies


3.0.0 (2014-12-23)
++++++++++++++++++

- upgrade external wakatime package to v3.0.0
- detect libraries and frameworks for C++, Java, .NET, PHP, and Python files


2.0.16 (2014-12-22)
+++++++++++++++++++

- upgrade external wakatime package to v2.1.11
- fix bug in offline logging when no response from api


2.0.15 (2014-12-05)
+++++++++++++++++++

- upgrade external wakatime package to v2.1.9
- fix bug preventing offline heartbeats from being purged after uploaded


2.0.14 (2014-12-04)
+++++++++++++++++++

- upgrade external wakatime package to v2.1.8
- fix UnicodeDecodeError when building user agent string
- handle case where response is None


2.0.13 (2014-11-30)
+++++++++++++++++++

- upgrade external wakatime package to v2.1.7
- upgrade pygments to v2.0.1
- always log an error when api key is incorrect


2.0.12 (2014-11-18)
+++++++++++++++++++

- upgrade external wakatime package to v2.1.6
- fix list index error when detecting subversion project


2.0.11 (2014-11-12)
+++++++++++++++++++

- upgrade external wakatime package to v2.1.4
- when Python was not compiled with https support, log an error to the log file


2.0.10 (2014-11-10)
+++++++++++++++++++

- upgrade external wakatime package to v2.1.3
- correctly detect branch for subversion projects


2.0.9 (2014-11-03)
++++++++++++++++++

- upgrade external wakatime package to v2.1.2
- catch UnicodeDecodeErrors to prevent error messages propegating into Vim


2.0.8 (2014-09-30)
++++++++++++++++++

- upgrade external wakatime package to v2.1.1
- fix bug where binary file opened as utf-8


2.0.7 (2014-09-30)
++++++++++++++++++

- upgrade external wakatime package to v2.1.0
- python3 compatibility changes


2.0.6 (2014-08-29)
++++++++++++++++++

- upgrade external wakatime package to v2.0.8
- supress output from svn command


2.0.5 (2014-08-07)
++++++++++++++++++

- upgrade external wakatime package to v2.0.6
- fix unicode bug by encoding json POST data


2.0.4 (2014-07-25)
++++++++++++++++++

- upgrade external wakatime package to v2.0.5
- use unique logger namespace to prevent collisions in shared plugin environments
- option in .wakatime.cfg to obfuscate file names


2.0.3 (2014-06-09)
++++++++++++++++++

- upgrade external wakatime package to v2.0.2


2.0.2 (2014-05-26)
++++++++++++++++++

- correctly exec wakatime-cli in Windows OS


2.0.1 (2014-05-26)
++++++++++++++++++

- upgrade external wakatime package to v2.0.1
- fix bug in queue preventing completed tasks from being purged


2.0.0 (2014-05-25)
++++++++++++++++++

- upgrade external wakatime package to v2.0.0
- offline time logging using sqlite3 to queue editor events


1.5.4 (2014-03-05)
++++++++++++++++++

- upgrade external wakatime package to v1.0.1
- use new domain wakatime.com


1.5.3 (2014-02-28)
++++++++++++++++++

- only save last action to ~/.wakatime.data when calling external wakatime-cli


1.5.2 (2014-02-05)
++++++++++++++++++

- upgrade external wakatime package to v1.0.0
- support for mercurial revision control


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
