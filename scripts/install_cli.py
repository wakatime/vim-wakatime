# -*- coding: utf-8 -*-


import contextlib
import json
import os
import platform
import re
import shutil
import ssl
import subprocess
import sys
import time
import traceback
from subprocess import PIPE
from zipfile import ZipFile

try:
    from ConfigParser import SafeConfigParser as ConfigParser
    from ConfigParser import Error as ConfigParserError
except ImportError:
    from configparser import ConfigParser, Error as ConfigParserError
try:
    from urllib2 import Request, urlopen, HTTPError
except ImportError:
    from urllib.request import Request, urlopen
    from urllib.error import HTTPError


def getOsName():
    osName = platform.system().lower()
    if osName.startswith('cygwin') or osName.startswith('mingw') or osName.startswith('msys'):
        return 'windows'
    if osName == 'linux' and 'ANDROID_DATA' in os.environ:
        return 'android'
    return osName


GITHUB_RELEASES_STABLE_URL = 'https://api.github.com/repos/wakatime/wakatime-cli/releases/latest'
GITHUB_DOWNLOAD_URL = 'https://github.com/wakatime/wakatime-cli/releases/latest/download'
PLUGIN = 'vim'

is_py2 = (sys.version_info[0] == 2)
is_py3 = (sys.version_info[0] == 3)
is_win = getOsName() == 'windows'

HOME_FOLDER = None
CONFIGS = None
INTERNAL_CONFIGS = None


def main(home=None):
    global CONFIGS, HOME_FOLDER

    if home:
        HOME_FOLDER = home

    CONFIGS = parseConfigFile(getConfigFile())

    if os.path.exists(os.path.join(getHomeFolder(), '.wakatime-internal.cfg')):
        try:
            os.remove(os.path.join(getHomeFolder(), '.wakatime-internal.cfg'))
        except:
            log(traceback.format_exc())

    if not os.path.exists(getResourcesFolder()):
        os.makedirs(getResourcesFolder())

    if not isCliLatest():
        downloadCLI()


if is_py2:
    import codecs
    open = codecs.open

    def u(text):
        if text is None:
            return None
        if isinstance(text, unicode):  # noqa: F821
            return text
        try:
            return text.decode('utf-8')
        except:
            try:
                return text.decode(sys.getdefaultencoding())
            except:
                try:
                    return unicode(text)  # noqa: F821
                except:
                    try:
                        return text.decode('utf-8', 'replace')
                    except:
                        try:
                            return unicode(str(text))  # noqa: F821
                        except:
                            return unicode('')  # noqa: F821

elif is_py3:
    def u(text):
        if text is None:
            return None
        if isinstance(text, bytes):
            try:
                return text.decode('utf-8')
            except:
                try:
                    return text.decode(sys.getdefaultencoding())
                except:
                    pass
        try:
            return str(text)
        except:
            return text.decode('utf-8', 'replace')

else:
    raise Exception('Unsupported Python version: {0}.{1}.{2}'.format(
        sys.version_info[0],
        sys.version_info[1],
        sys.version_info[2],
    ))


class Popen(subprocess.Popen):
    """Patched Popen to prevent opening cmd window on Windows platform."""

    def __init__(self, *args, **kwargs):
        if is_win:
            startupinfo = kwargs.get('startupinfo')
            try:
                startupinfo = startupinfo or subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            except AttributeError:
                pass
            kwargs['startupinfo'] = startupinfo
        super(Popen, self).__init__(*args, **kwargs)


def parseConfigFile(configFile):
    """Returns a configparser.SafeConfigParser instance with configs
    read from the config file. Default location of the config file is
    at ~/.wakatime.cfg.
    """

    kwargs = {} if is_py2 else {'strict': False}
    configs = ConfigParser(**kwargs)
    try:
        with open(configFile, 'r', encoding='utf-8') as fh:
            try:
                if is_py2:
                    configs.readfp(fh)
                else:
                    configs.read_file(fh)
                return configs
            except ConfigParserError:
                print(traceback.format_exc())
                return configs
    except IOError:
        return configs


def log(message, *args, **kwargs):
    if not CONFIGS.has_option('settings', 'debug') or CONFIGS.get('settings', 'debug') != 'true':
        return
    msg = message
    if len(args) > 0:
        msg = message.format(*args)
    elif len(kwargs) > 0:
        msg = message.format(**kwargs)
    try:
        print('[WakaTime Install] {msg}'.format(msg=msg))
    except UnicodeDecodeError:
        print(u('[WakaTime Install] {msg}').format(msg=u(msg)))


def getHomeFolder():
    global HOME_FOLDER

    if not HOME_FOLDER:
        if len(sys.argv) == 2:
            HOME_FOLDER = sys.argv[-1]
        else:
            HOME_FOLDER = os.path.realpath(os.environ.get('WAKATIME_HOME') or os.path.expanduser('~'))

    return HOME_FOLDER


def getResourcesFolder():
    return os.path.join(getHomeFolder(), '.wakatime')


def getConfigFile(internal=None):
    if internal:
        return os.path.join(getResourcesFolder(), 'wakatime-internal.cfg')
    return os.path.join(getHomeFolder(), '.wakatime.cfg')


def downloadCLI():
    log('Downloading wakatime-cli...')

    if os.path.isdir(os.path.join(getResourcesFolder(), 'wakatime-cli')):
        shutil.rmtree(os.path.join(getResourcesFolder(), 'wakatime-cli'))

    try:
        url = cliDownloadUrl()
        log('Downloading wakatime-cli from {url}'.format(url=url))
        zip_file = os.path.join(getResourcesFolder(), 'wakatime-cli.zip')
        download(url, zip_file)

        if isCliInstalled():
            try:
                os.remove(getCliLocation())
            except:
                log(traceback.format_exc())
        if isCliLinked():
            try:
                os.remove(getSymlinkLocation())
            except:
                log(traceback.format_exc())

        log('Extracting wakatime-cli...')
        with contextlib.closing(ZipFile(zip_file)) as zf:
            zf.extractall(getResourcesFolder())

        if not is_win:
            os.chmod(getCliLocation(), 509)  # 755

        try:
            os.remove(os.path.join(getResourcesFolder(), 'wakatime-cli.zip'))
        except:
            log(traceback.format_exc())
    except:
        log(traceback.format_exc())

    createSymlink()

    log('Finished extracting wakatime-cli.')


WAKATIME_CLI_LOCATION = None


def getCliLocation():
    global WAKATIME_CLI_LOCATION

    if not WAKATIME_CLI_LOCATION:
        binary = 'wakatime-cli-{osname}-{arch}{ext}'.format(
            osname=getOsName(),
            arch=architecture(),
            ext='.exe' if is_win else '',
        )
        WAKATIME_CLI_LOCATION = os.path.join(getResourcesFolder(), binary)

    return WAKATIME_CLI_LOCATION


def getSymlinkLocation():
    binary = 'wakatime-cli{ext}'.format(
        ext='.exe' if is_win else '',
    )
    return os.path.join(getResourcesFolder(), binary)


def architecture():
    arch = platform.machine() or platform.processor()
    if arch == 'armv7l':
        return 'arm'
    if arch == 'aarch64':
        return 'arm64'
    if 'arm' in arch:
        return 'arm64' if sys.maxsize > 2**32 else 'arm'
    if getOsName() == "darwin":
        uname = appleUname()
        if uname:
            return uname
    return 'amd64' if sys.maxsize > 2**32 else '386'


def appleUname():
    try:
        folder = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        folder = os.getcwd()

    args = [os.path.join(folder, 'uname')]

    try:
        stdout, stderr = Popen(args, stdout=PIPE, stderr=PIPE).communicate()
    except:
        return None

    stdout = ((stdout or b'') + (stderr or b'')).decode('utf-8').strip()
    if not stdout:
        return None

    return stdout


def isCliInstalled():
    return os.path.exists(getCliLocation())


def isCliLinked():
    return os.path.exists(getSymlinkLocation())


def isCliLatest():
    if not isCliInstalled() or not isCliLinked():
        return False

    args = [getCliLocation(), '--version']
    try:
        stdout, stderr = Popen(args, stdout=PIPE, stderr=PIPE).communicate()
    except:
        return False
    stdout = (stdout or b'') + (stderr or b'')
    localVer = extractVersion(stdout.decode('utf-8'))
    if not localVer:
        log('Local wakatime-cli version not found.')
        return False
    if localVer == "<local-build>":
        log('Local wakatime-cli version is <local-build>, skip updating.')
        return True

    log('Current wakatime-cli version is %s' % localVer)

    configs, last_accessed = None, None
    try:
        configs = parseConfigFile(getConfigFile(True))
        if configs and configs.has_option('internal', 'cli_version_last_accessed'):
            last_accessed = configs.get('internal', 'cli_version_last_accessed')
    except:
        log(traceback.format_exc())

    if last_accessed:
        try:
            last_accessed = int(float(last_accessed))
        except:
            last_accessed = None
        now = round(time.time())
        four_hours = 4 * 3600
        if last_accessed and last_accessed + four_hours > now:
            log('Skip checking for wakatime-cli updates because recently checked {0} seconds ago.'.format(now - last_accessed))
            return True

    log('Checking for updates to wakatime-cli...')
    remoteVer = getLatestCliVersion()

    if not remoteVer:
        return True

    if remoteVer == localVer:
        log('wakatime-cli is up to date.')
        return True

    log('Found an updated wakatime-cli %s' % remoteVer)
    return False


def getLatestCliVersion():
    try:
        headers, contents, code = request(GITHUB_RELEASES_STABLE_URL)

        log('GitHub API Response {0}'.format(code))

        data = json.loads(contents.decode('utf-8'))

        ver = data['tag_name']
        log('Latest wakatime-cli version from GitHub: {0}'.format(ver))

        try:
            configs = parseConfigFile(getConfigFile(True))
        except:
            log(traceback.format_exc())
        if configs:
            last_modified = headers.get('Last-Modified')
            if not configs.has_section('internal'):
                configs.add_section('internal')
            configs.set('internal', 'cli_version', str(u(ver)))
            configs.set('internal', 'cli_version_last_modified', str(u(last_modified)))
            configs.set('internal', 'cli_version_last_accessed', str(round(time.time())))
            with open(getConfigFile(True), 'w', encoding='utf-8') as fh:
                configs.write(fh)

        return ver
    except:
        log(traceback.format_exc())
        return None


def extractVersion(text):
    pattern = re.compile(r"([0-9]+\.[0-9]+\.[0-9]+)")
    match = pattern.search(text)
    if match:
        return 'v{ver}'.format(ver=match.group(1))
    if text and text.strip() == "<local-build>":
        return "<local-build>"
    return None


def cliDownloadUrl():
    osname = getOsName()
    arch = architecture()

    validCombinations = [
      'android-arm',
      'android-arm64',
      'darwin-amd64',
      'darwin-arm64',
      'freebsd-386',
      'freebsd-amd64',
      'freebsd-arm',
      'linux-386',
      'linux-amd64',
      'linux-arm',
      'linux-arm64',
      'netbsd-386',
      'netbsd-amd64',
      'netbsd-arm',
      'openbsd-386',
      'openbsd-amd64',
      'openbsd-arm',
      'openbsd-arm64',
      'windows-386',
      'windows-amd64',
      'windows-arm64',
    ]
    check = '{osname}-{arch}'.format(osname=osname, arch=arch)
    if check not in validCombinations:
        reportMissingPlatformSupport(osname, arch)

    return '{prefix}/wakatime-cli-{osname}-{arch}.zip'.format(
        prefix=GITHUB_DOWNLOAD_URL,
        osname=osname,
        arch=arch,
    )


def reportMissingPlatformSupport(osname, arch):
    url = 'https://api.wakatime.com/api/v1/cli-missing?osname={osname}&architecture={arch}&plugin={plugin}'.format(
        osname=osname,
        arch=arch,
        plugin=PLUGIN,
    )
    request(url)


def request(url):
    req = Request(url)
    req.add_header('User-Agent', 'github.com/wakatime/{plugin}-wakatime'.format(plugin=PLUGIN))

    proxy = CONFIGS.get('settings', 'proxy') if CONFIGS.has_option('settings', 'proxy') else None
    if proxy:
        req.set_proxy(proxy, 'https')

    try:
        resp = urlopen(req)
        try:
            headers = dict(resp.getheaders())
        except:
            headers = dict(resp.headers)
        return headers, resp.read(), resp.getcode()
    except HTTPError as err:
        if err.code == 304:
            return None, None, 304
        if is_py2:
            with SSLCertVerificationDisabled():
                try:
                    resp = urlopen(req)
                    try:
                        headers = dict(resp.getheaders())
                    except:
                        headers = dict(resp.headers)
                    return headers, resp.read(), resp.getcode()
                except HTTPError as err2:
                    if err2.code == 304:
                        return None, None, 304
                    log(err.read().decode())
                    log(err2.read().decode())
                    raise
                except IOError:
                    raise
        log(err.read().decode())
        raise
    except IOError:
        if is_py2:
            with SSLCertVerificationDisabled():
                try:
                    resp = urlopen(url)
                    try:
                        headers = dict(resp.getheaders())
                    except:
                        headers = dict(resp.headers)
                    return headers, resp.read(), resp.getcode()
                except HTTPError as err:
                    if err.code == 304:
                        return None, None, 304
                    log(err.read().decode())
                    raise
                except IOError:
                    raise
        raise


def download(url, filePath):
    req = Request(url)
    req.add_header('User-Agent', 'github.com/wakatime/{plugin}-wakatime'.format(plugin=PLUGIN))

    proxy = CONFIGS.get('settings', 'proxy') if CONFIGS.has_option('settings', 'proxy') else None
    if proxy:
        req.set_proxy(proxy, 'https')

    with open(filePath, 'wb') as fh:
        try:
            resp = urlopen(req)
            fh.write(resp.read())
        except HTTPError as err:
            if err.code == 304:
                return None, None, 304
            if is_py2:
                with SSLCertVerificationDisabled():
                    try:
                        resp = urlopen(req)
                        fh.write(resp.read())
                        return
                    except HTTPError as err2:
                        log(err.read().decode())
                        log(err2.read().decode())
                        raise
                    except IOError:
                        raise
            log(err.read().decode())
            raise
        except IOError:
            if is_py2:
                with SSLCertVerificationDisabled():
                    try:
                        resp = urlopen(url)
                        fh.write(resp.read())
                        return
                    except HTTPError as err:
                        log(err.read().decode())
                        raise
                    except IOError:
                        raise
            raise


def is_symlink(path):
    try:
        return os.is_symlink(path)
    except:
        return False


def createSymlink():
    link = getSymlinkLocation()
    if os.path.exists(link) and is_symlink(link):
        return  # don't re-create symlink on Unix-like platforms

    if os.path.isdir(link):
        shutil.rmtree(link)
    elif os.path.isfile(link):
        os.remove(link)

    try:
        os.symlink(getCliLocation(), link)
        if not isCliLinked():
            raise Exception('Link not created.')
    except:
        log(traceback.format_exc())
        log('Unable to create symlink, will copy instead.')
        try:
            shutil.copy2(getCliLocation(), link)
            if not isCliLinked():
                raise Exception('File not copied.')
            if not is_win:
                os.chmod(link, 509)  # 755
        except:
            log(traceback.format_exc())
            log('Unable to use copy2, will use copyfile.')
            try:
                shutil.copyfile(getCliLocation(), link)
                if not isCliLinked():
                    raise Exception('File not copied.')
                if not is_win:
                    os.chmod(link, 509)  # 755
            except:
                log(traceback.format_exc())
                log('Unable to install wakatime-cli.')


class SSLCertVerificationDisabled(object):

    def __enter__(self):
        self.original_context = ssl._create_default_https_context
        ssl._create_default_https_context = ssl._create_unverified_context

    def __exit__(self, *args, **kwargs):
        ssl._create_default_https_context = self.original_context


if __name__ == '__main__':
    main()
    sys.exit(0)
