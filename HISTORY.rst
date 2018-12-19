
History
-------


7.1.3 (2018-12-19)
++++++++++++++++++
- Upgrade wakatime-cli to v10.6.1.
- Correctly parse include_only_with_project_file when set to false.
  `wakatime#161 <https://github.com/wakatime/wakatime/issues/161>`_
- Support language argument for non-file entity types.
- Send 25 heartbeats per API request.
- New category "Writing Tests".
  `wakatime#156 <https://github.com/wakatime/wakatime/issues/156>`_
- Fix bug caused by git config section without any submodule option defined.
  `wakatime#152 <https://github.com/wakatime/wakatime/issues/152>`_


7.1.2 (2018-09-20)
++++++++++++++++++

- Upgrade wakatime-cli to v10.2.4.
- Default --sync-offline-activity to 100 instead of 5, so offline coding is
  synced to dashboard faster.
- Batch heartbeats in groups of 10 per api request.
- New config hide_project_name and argument --hide-project-names for
  obfuscating project names when sending coding activity to api.
- Fix mispelled Gosu language.
  `wakatime#137 <https://github.com/wakatime/wakatime/issues/137>`_
- Remove metadata when hiding project or file names.
- New --local-file argument to be used when --entity is a remote file.
- New argument --sync-offline-activity for configuring the maximum offline
  heartbeats to sync to the WakaTime API.
- Support for project detection from git worktree folders.
- Force forward slash for file paths.
- New --category argument.
- New --exclude-unknown-project argument and corresponding config setting.


7.1.1 (2018-04-04)
++++++++++++++++++

- Force forward slash for wakatime-cli path on Windows.
  `#56 <https://github.com/wakatime/vim-wakatime/issues/56>`_


7.1.0 (2018-04-03)
++++++++++++++++++

- Detect python binary from common paths.


7.0.7 (2018-03-15)
++++++++++++++++++

- Upgrade wakatime-cli to v10.1.3.
- Smarter C vs C++ vs Objective-C language detection.


7.0.6 (2018-03-15)
++++++++++++++++++

- Upgrade wakatime-cli to v10.1.2.
- Detect dependencies from Swift, Objective-C, TypeScript and JavaScript files.
- Categorize .mjs files as JavaScript.
  `wakatime#121 <https://github.com/wakatime/wakatime/issues/121>`_
- Detect dependencies from Elm, Haskell, Haxe, Kotlin, Rust, and Scala files.
- Improved Matlab vs Objective-C language detection.
  `wakatime#129 <https://github.com/wakatime/wakatime/issues/129>`_


7.0.5 (2018-01-28)
++++++++++++++++++

- Correctly handle async output in Neovim as list not string.
  `#62 <https://github.com/wakatime/vim-wakatime/issues/62>`_


7.0.4 (2018-01-04)
++++++++++++++++++

- Upgrade wakatime-cli to v10.1.0.
- Ability to only track folders containing a .wakatime-project file using new
  include_only_with_project_file argument and config option.
- Fix bug that caused heartbeats to be cached locally instead of sent to API.


7.0.3 (2017-11-23)
++++++++++++++++++

- Upgrade wakatime-cli to v10.0.4.
- Improve Java dependency detection.
- Skip null or missing heartbeats from extra heartbeats argument.


7.0.2 (2017-11-22)
++++++++++++++++++

- Upgrade wakatime-cli to v10.0.3.
- Limit bulk syncing to 5 heartbeats per request.
  `wakatime#109 <https://github.com/wakatime/wakatime/issues/109>`_
- Support saving unicode heartbeats when working offline.
  `wakatime#112 <https://github.com/wakatime/wakatime/issues/112>`_


7.0.1 (2017-11-09)
++++++++++++++++++

- Upgrade wakatime-cli to v10.0.1.
- Parse array of results from bulk heartbeats endpoint, only saving heartbeats
  to local offline cache when they were not accepted by the api.


7.0.0 (2017-11-08)
++++++++++++++++++

- Upgrade wakatime-cli to v10.0.0.
- Upload multiple heartbeats to bulk endpoint for improved network performance.
  `wakatime#107 <https://github.com/wakatime/wakatime/issues/107>`_
- Fix bug causing 401 response when hidefilenames is enabled.
  `wakatime#106 <https://github.com/wakatime/wakatime/issues/106>`_
- Detect project and branch names from git submodules.
  `wakatime#105 <https://github.com/wakatime/wakatime/issues/105>`_

6.0.3 (2017-10-29)
++++++++++++++++++

- Upgrade wakatime-cli to v8.0.5.
- Allow passing string arguments wrapped in extra quotes for plugins which
  cannot properly escape spaces in arguments.
- Upgrade pytz to v2017.2.
- Upgrade requests to v2.18.4.
- Upgrade tzlocal to v1.4.
- Use WAKATIME_HOME env variable for offline and session caching.
  `wakatime#102 <https://github.com/wakatime/wakatime/issues/102>`_


6.0.2 (2017-10-19)
++++++++++++++++++

- Only use async when Vim supports options passed to job_start function.
  `#54 <https://github.com/wakatime/vim-wakatime/issues/54>`_
- Support vimrc changing Vim shell by temporarily overwriting &shell.
  `#55 <https://github.com/wakatime/vim-wakatime/issues/55>`_


6.0.1 (2017-10-04)
++++++++++++++++++

- Support for async in Neovim.
- Support for Vim async on Windows.


6.0.0 (2017-10-04)
++++++++++++++++++

- Bug fix for extra heartbeats time containing multiple decimal point chars
  which prevented extra heartbeats from being sent.
- Support running wakatime-cli async in Vim 8.0+. This greatly improves
  performance and prevents screen artifacts and the need to redraw.
  `#53 <https://github.com/wakatime/vim-wakatime/issues/53>`_
- Upgrade wakatime-cli to v8.0.3.
- Improve Matlab language detection.


5.0.2 (2017-05-25)
++++++++++++++++++

- Ability to disable screen redraw for improved performance.
- Make sure buffered heartbeats keep correct ordering.
- Compatibility with older Vim versions that do not support quitpre.
  `#49 <https://github.com/wakatime/vim-wakatime/issues/49>`_
- Prevent sending a heartbeat when first opening Vim for imporved startup time.
- Prevent wildcard option from breaking expand() when Vim is launched from a
  wildcard folder.
  `#50 <https://github.com/wakatime/vim-wakatime/issues/50>`_
- Upgrade wakatime-cli to v8.0.2.
- Only treat proxy string as NTLM proxy after unable to connect with HTTPS and
  SOCKS proxy.
- Support running automated tests on Linux, OS X, and Windows.
- Ability to disable SSL cert verification. wakatime/wakatime
- Disable line count stats for files larger than 2MB to improve performance.
- Print error saying Python needs upgrading when requests can't be imported.


5.0.1 (2017-04-24)
++++++++++++++++++

- Use localtime() when reltime() not available.
  `#48 <https://github.com/wakatime/vim-wakatime/issues/48>`_


5.0.0 (2017-04-23)
++++++++++++++++++

- Buffer heartbeats and send to wakatime-cli only once per 10 seconds.
  `#47 <https://github.com/wakatime/vim-wakatime/issues/47>`_
  `#45 <https://github.com/wakatime/vim-wakatime/issues/45>`_
- New :WakaTimeApiKey, :WakaTimeDebugEnable, :WakaTimeDebugDisable commands.
- Improve INI config file parsing so api key check is more robust.
  `#46 <https://github.com/wakatime/vim-wakatime/issues/46>`_


4.0.15 (2017-04-13)
++++++++++++++++++

- Detect debug setting from ~/.wakatime.cfg file
- Support $WAKATIME_HOME env variable for setting path to config and log files.
- Upgrade wakatime-cli to v8.0.0.
- Allow colons in [projectmap] config section.
- Increase priority of F# and TypeScript languages.


4.0.14 (2017-02-20)
++++++++++++++++++

- Upgrade wakatime-cli to v7.0.2.
- Language detected by Vim now overwrites auto-detected language, if the Vim
  language is supported in default.json or vim.json.
- Support NTLM proxy format like domain\\user:pass.
- Support for Python 3.6.


4.0.13 (2017-02-13)
++++++++++++++++++

- Upgrade wakatime-cli to v6.2.2.
- Allow boolean or list of regex patterns for hidefilenames config setting.
- New WAKATIME_HOME env variable for setting path to config and log files.
- New hostname setting in config file to set machine hostname. Hostname
  argument takes priority over hostname from config file.
- Improve debug warning message from unsupported dependency parsers.
- Handle exception from Python system library read permission problem.
- Prevent encoding errors when logging files with special characters.
- Handle unknown exceptions from requests library by deleting cached session
  object because it could be from a previous conflicting version.
- Prevent logging unrelated exception when logging tracebacks.


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

- Upgrade wakatime-cli to v4.1.13
- Encode TimeZone as utf-8 before adding to headers
- Encode X-Machine-Name as utf-8 before adding to headers


4.0.7 (2016-01-11)
++++++++++++++++++

- Upgrade wakatime cli to v4.1.10
- Improve C# dependency detection
- Correctly log exception tracebacks
- Log all unknown exceptions to wakatime.log file
- Disable urllib3 SSL warning from every request
- Detect dependencies from golang files
- Use api.wakatime.com for sending heartbeats
- Accept 201 or 202 response codes as success from api
- Upgrade requests package to v2.9.1


4.0.6 (2015-12-01)
++++++++++++++++++

- Upgrade wakatime cli to v4.1.8
- Default request timeout of 30 seconds
- New --timeout command line argument to change request timeout in seconds
- Fix bug in guess_language function
- Improve dependency detection


4.0.5 (2015-09-07)
++++++++++++++++++

- Upgrade wakatime cli to v4.1.6
- Fix bug in offline caching which prevented heartbeats from being cleaned up
- Fix local session caching
- New --entity and --entitytype command line arguments
- Fix entry point for pypi distribution
- Allow passing command line arguments using sys.argv


4.0.4 (2015-08-25)
++++++++++++++++++

- Upgrade wakatime cli to v4.1.1
- Send hostname in X-Machine-Name header
- Catch exceptions from pygments.modeline.get_filetype_from_buffer
- Upgrade requests package to v2.7.0
- Handle non-ASCII characters in import path on Windows, won't fix for Python2
- Upgrade argparse to v1.3.0
- Move language translations to api server
- Move extension rules to api server
- Detect correct header file language based on presence of .cpp or .c files
  named the same as the .h file.


4.0.3 (2015-06-23)
++++++++++++++++++

- Fix offline logging
- Limit language detection to known file extensions, unless file contents has
  a vim modeline.
- Upgrade wakatime cli to v4.0.16


4.0.2 (2015-06-11)
++++++++++++++++++

- Upgrade wakatime cli to v4.0.15
- Guess language using multiple methods, then use most accurate guess
- Use entity and type for new heartbeats api resource schema


4.0.1 (2015-05-31)
++++++++++++++++++

- Upgrade wakatime cli to v4.0.14
- Make sure config file has api_key
- Only display setup complete message first time setting up cfg file
- Don't log time towards git temporary files
- Prevent slowness in quickfix window to fix.
  `#24 <https://github.com/wakatime/vim-wakatime/issues/24>`_
- Reuse SSL connection across multiple processes for improved performance
- Correctly display caller and lineno in log file when debug is true
- Project passed with --project argument will always be used
- New --alternate-project argument
- Fix bug with auto detecting project name
- Correctly log message from py.warnings module
- Handle plugin_directory containing spaces


4.0.0 (2015-05-01)
++++++++++++++++++

- Upgrade wakatime cli to v4.0.8
- Check for api_key in config file instead of just checking if file exists


3.0.9 (2015-04-02)
++++++++++++++++++

- Upgrade wakatime cli to v4.0.7
- Update requests package to v2.0.6
- Update simplejson to v3.6.5
- Capture warnings in log file


3.0.8 (2015-03-09)
++++++++++++++++++

- Upgrade wakatime cli to v4.0.4
- New options for excluding and including directories


3.0.7 (2015-02-12)
++++++++++++++++++

- Upgrade external wakatime-cli to v4.0.0
- Use requests library instead of urllib2, so api SSL cert is verified
- New proxy config file item for https proxy support


3.0.6 (2015-01-19)
++++++++++++++++++

- Prompt for api key only after first buffer window opened
- Include vim version number in plugin user agent string


3.0.5 (2015-01-13)
++++++++++++++++++

- Upgrade external wakatime package to v3.0.5
- Ignore errors from malformed markup (too many closing tags)


3.0.4 (2015-01-06)
++++++++++++++++++

- Upgrade external wakatime package to v3.0.4
- Remove unused dependency, which is missing in some python environments


3.0.3 (2014-12-25)
++++++++++++++++++

- Upgrade external wakatime package to v3.0.3
- Detect JavaScript frameworks from script tags in Html template files


3.0.2 (2014-12-25)
++++++++++++++++++

- Upgrade external wakatime package to v3.0.2
- Detect frameworks from JavaScript and JSON files


3.0.1 (2014-12-23)
++++++++++++++++++

- Upgrade external wakatime package to v3.0.1
- Handle unknown language when parsing dependencies


3.0.0 (2014-12-23)
++++++++++++++++++

- Upgrade external wakatime package to v3.0.0
- Detect libraries and frameworks for C++, Java, .NET, PHP, and Python files


2.0.16 (2014-12-22)
+++++++++++++++++++

- Upgrade external wakatime package to v2.1.11
- Fix bug in offline logging when no response from api


2.0.15 (2014-12-05)
+++++++++++++++++++

- Upgrade external wakatime package to v2.1.9
- Fix bug preventing offline heartbeats from being purged after uploaded


2.0.14 (2014-12-04)
+++++++++++++++++++

- Upgrade external wakatime package to v2.1.8
- Fix UnicodeDecodeError when building user agent string
- Handle case where response is None


2.0.13 (2014-11-30)
+++++++++++++++++++

- Upgrade external wakatime package to v2.1.7
- Upgrade pygments to v2.0.1
- Always log an error when api key is incorrect


2.0.12 (2014-11-18)
+++++++++++++++++++

- Upgrade external wakatime package to v2.1.6
- Fix list index error when detecting subversion project


2.0.11 (2014-11-12)
+++++++++++++++++++

- Upgrade external wakatime package to v2.1.4
- When Python was not compiled with https support, log an error to the log file


2.0.10 (2014-11-10)
+++++++++++++++++++

- Upgrade external wakatime package to v2.1.3
- Correctly detect branch for subversion projects


2.0.9 (2014-11-03)
++++++++++++++++++

- Upgrade external wakatime package to v2.1.2
- Catch UnicodeDecodeErrors to prevent error messages propegating into Vim


2.0.8 (2014-09-30)
++++++++++++++++++

- Upgrade external wakatime package to v2.1.1
- Fix bug where binary file opened as utf-8


2.0.7 (2014-09-30)
++++++++++++++++++

- Upgrade external wakatime package to v2.1.0
- Python3 compatibility changes


2.0.6 (2014-08-29)
++++++++++++++++++

- Upgrade external wakatime package to v2.0.8
- Supress output from svn command


2.0.5 (2014-08-07)
++++++++++++++++++

- Upgrade external wakatime package to v2.0.6
- Fix unicode bug by encoding json POST data


2.0.4 (2014-07-25)
++++++++++++++++++

- Upgrade external wakatime package to v2.0.5
- Use unique logger namespace to prevent collisions in shared plugin
  environments.
- Option in .wakatime.cfg to obfuscate file names


2.0.3 (2014-06-09)
++++++++++++++++++

- Upgrade external wakatime package to v2.0.2


2.0.2 (2014-05-26)
++++++++++++++++++

- Correctly exec wakatime-cli in Windows OS


2.0.1 (2014-05-26)
++++++++++++++++++

- Upgrade external wakatime package to v2.0.1
- Fix bug in queue preventing completed tasks from being purged


2.0.0 (2014-05-25)
++++++++++++++++++

- Upgrade external wakatime package to v2.0.0
- Offline time logging using sqlite3 to queue editor events


1.5.4 (2014-03-05)
++++++++++++++++++

- Upgrade external wakatime package to v1.0.1
- Use new domain wakatime.com


1.5.3 (2014-02-28)
++++++++++++++++++

- Only save last action to ~/.wakatime.data when calling external wakatime-cli


1.5.2 (2014-02-05)
++++++++++++++++++

- Upgrade external wakatime package to v1.0.0
- Support for mercurial revision control


1.5.1 (2014-01-15)
++++++++++++++++++

- Upgrade external wakatime package to v0.5.3
- Bug fix for unicode in Python3


1.5.0 (2013-12-16)
++++++++++++++++++

- Upgrade external wakatime package to v0.5.1
- Fix MAXREPEAT bug in Python2.7 by not using python in VimL


1.4.0 (2013-12-13)
++++++++++++++++++

- Upgrade external wakatime package to v0.5.0
- Convert ~/.wakatime.conf to ~/.wakatime.cfg and use configparser format


1.3.1 (2013-12-02)
++++++++++++++++++

- Support non-English characters in file names


1.3.0 (2013-11-28)
++++++++++++++++++

- Increase frequency of pings to api from every 5 mins to every 2 mins
- Upgrade external wakatime package to v0.4.10
- Support .wakatime-project files for custom project names


1.2.3 (2013-10-27)
++++++++++++++++++

- Upgrade external wakatime package to v0.4.9
- New config file option to ignore and prevent logging files based on regex


1.2.2 (2013-10-13)
++++++++++++++++++

- Upgrade external wakatime package to v0.4.8
- Prevent popup windows when detecting Git project on Windows platform


1.2.1 (2013-09-30)
++++++++++++++++++

- Upgrade external wakatime package to v0.4.7
- Send local olson timezone string in api requests


1.2.0 (2013-09-22)
++++++++++++++++++

- Upgrade external wakatime package to v0.4.6
- Logging total lines in current file and language used


1.1.5 (2013-09-07)
++++++++++++++++++

- Upgrade external wakatime package to v0.4.5
- Fix relative import error by adding packages directory to sys path


1.1.4 (2013-09-06)
++++++++++++++++++

- Upgrade external wakatime package to v0.4.4
- Use urllib2 again because of problems sending json with requests module


1.1.3 (2013-09-04)
++++++++++++++++++

- Upgrade external wakatime package to v0.4.3


1.1.2 (2013-09-04)
++++++++++++++++++

- Upgrade external wakatime package to v0.4.2


1.1.1 (2013-08-25)
++++++++++++++++++

- Upgrade external wakatime package to v0.4.1


1.1.0 (2013-08-15)
++++++++++++++++++

- Upgrade external wakatime package to v0.4.0
- Detect branch from revision control


1.0.0 (2013-08-12)
++++++++++++++++++

- Upgrade external wakatime package to v0.3.1
- Use requests module instead of urllib2 to verify SSL certs


0.2.6 (2013-07-29)
++++++++++++++++++

- Upgrade external wakatime package to v0.2.0 for python2 and python3 support


0.2.5 (2013-07-22)
++++++++++++++++++

- Upgrade external wakatime package to v0.1.4
- Use timeout and api pings to calculate logged time server-side instead of
  sending end_time


0.2.4 (2013-07-20)
++++++++++++++++++

- Upgrade external wakatime package to v0.1.3
- Run external wakatime script with any python version instead of forcing
  python2
- Support for Subversion projects


0.2.3 (2013-07-16)
++++++++++++++++++

- Fix bug when calculation away duration
- Fixed bug where away prompt would do the opposite of user's choice
- Force external wakatime script to run with python2
- Many bug fixes


0.2.2 (2013-07-10)
++++++++++++++++++

- Fix bug where event missed when first opening Vim with a file
- Remove verbose flag to stop printing debug messages
- Stop using VimL strings as floats
- Only log events once every 5 minutes, except for write events
- Prompt user for api key if one does not already exist
- Set 5 second delay between writing last cursor event time to local file
- Many bug fixes


0.2.1 (2013-07-07)
++++++++++++++++++

- Move api interface code into external wakatime repository
- Support for Git projects
- Support changes to api schema which break backwards compatibility
- Simplify user events into regular events and write events


0.1.3 (2013-07-02)
++++++++++++++++++

- Move wakatime.log to $HOME folder
- Support Vim's +clientserver for multiple instances of Vim
- Auto create log file if it does not exist
- Fixed bugs


0.1.2 (2013-06-25)
++++++++++++++++++

- Birth
