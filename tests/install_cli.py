"""Run installer regressions with python3 tests/install_cli.py."""

import errno
import importlib.util
import io
import ntpath
import os
from pathlib import Path
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch
from zipfile import ZipFile


INSTALLER = Path(__file__).resolve().parents[1] / 'scripts' / 'install_cli.py'


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='wakatime-installer-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.home = self.root / 'home with spaces'
        self.home.mkdir()
        self.legacy = self.home / '.wakatime.cfg'
        self.xdg_home = self.root / 'xdg with spaces'
        self.xdg = self.xdg_home / 'wakatime' / 'wakatime.cfg'
        self.default_xdg = self.home / '.config' / 'wakatime' / 'wakatime.cfg'
        env = patch.dict(os.environ, {
            'HOME': str(self.home),
            'USERPROFILE': str(self.home),
            'XDG_CONFIG_HOME': str(self.xdg_home),
        }, clear=True)
        env.start()
        self.addCleanup(env.stop)
        argv = patch.object(sys, 'argv', [str(INSTALLER)])
        argv.start()
        self.addCleanup(argv.stop)
        spec = importlib.util.spec_from_file_location('wakatime_installer', INSTALLER)
        self.installer = importlib.util.module_from_spec(spec)
        with patch.object(sys, 'dont_write_bytecode', True):
            spec.loader.exec_module(self.installer)

    def write_config(self, path, proxy='proxy.example:8080'):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('[settings]\nproxy = ' + proxy + '\n', encoding='utf-8')

    def check_config(self, expected, proxy='proxy.example:8080'):
        self.assertEqual(self.installer.getConfigFile(), str(expected))
        configs = self.installer.parseConfigFile(self.installer.getConfigFile())
        if proxy is None:
            self.assertFalse(configs.has_option('settings', 'proxy'))
        else:
            self.assertEqual(configs.get('settings', 'proxy'), proxy)

    def test_custom_xdg(self):
        self.write_config(self.xdg)
        self.check_config(self.xdg)

    def test_default_xdg(self):
        del os.environ['XDG_CONFIG_HOME']
        self.write_config(self.default_xdg)
        self.check_config(self.default_xdg)

    def test_nonabsolute_xdg_uses_default(self):
        self.write_config(self.default_xdg)
        for value in ('', 'relative-config', '~/config'):
            with self.subTest(value=value):
                os.environ['XDG_CONFIG_HOME'] = value
                self.check_config(self.default_xdg)

    def test_windows_xdg_requires_volume_absolute_path(self):
        # Python 3.12 and earlier consider a single leading separator absolute.
        def old_isabs(path):
            return path in ('/config', '\\config') or ntpath.isabs(path)

        windows_os = SimpleNamespace(
            name='nt',
            environ={},
            path=SimpleNamespace(join=ntpath.join, isabs=old_isabs),
            stat=Mock(side_effect=OSError(errno.ENOENT, 'Missing legacy config')),
        )
        self.installer.HOME_FOLDER = r'C:\Users\tester'
        default = r'C:\Users\tester\.config\wakatime\wakatime.cfg'
        cases = {
            '': default,
            '/config': default,
            '\\config': default,
            r'C:config': default,
            r'config': default,
            r'C:\config': r'C:\config\wakatime\wakatime.cfg',
            'C:/config': 'C:/config\\wakatime\\wakatime.cfg',
            r'\\server\share\config': r'\\server\share\config\wakatime\wakatime.cfg',
            '//server/share/config': '//server/share/config\\wakatime\\wakatime.cfg',
        }
        with patch.object(self.installer, 'os', windows_os), \
                patch.object(self.installer, 'is_win', True):
            for value, expected in cases.items():
                with self.subTest(value=value):
                    windows_os.environ['XDG_CONFIG_HOME'] = value
                    self.assertEqual(self.installer.getConfigFile(), expected)

    def test_empty_wakatime_home_uses_xdg(self):
        os.environ['WAKATIME_HOME'] = ''
        self.write_config(self.xdg)
        self.check_config(self.xdg)

    def test_wakatime_home_precedes_xdg(self):
        home = self.root / 'explicit home'
        os.environ['WAKATIME_HOME'] = str(home)
        config = home / '.wakatime.cfg'
        self.write_config(config)
        self.write_config(self.xdg, 'xdg.example:8080')
        self.check_config(config)

    def test_wakatime_home_without_config_stays_legacy(self):
        home = self.root / 'missing explicit home'
        os.environ['WAKATIME_HOME'] = str(home)
        self.write_config(self.xdg)
        self.check_config(home / '.wakatime.cfg', proxy=None)
        self.assertFalse(home.exists())

    def test_legacy_precedes_xdg(self):
        self.write_config(self.legacy)
        self.write_config(self.xdg, 'xdg.example:8080')
        self.check_config(self.legacy)

    def test_empty_legacy_precedes_xdg(self):
        self.legacy.touch()
        self.write_config(self.xdg)
        self.check_config(self.legacy, proxy=None)

    @unittest.skipIf(os.name == 'nt', 'Unix file permissions')
    def test_unreadable_legacy_precedes_xdg(self):
        self.write_config(self.legacy)
        self.write_config(self.xdg)
        self.legacy.chmod(0)
        self.addCleanup(self.legacy.chmod, 0o600)
        if os.access(self.legacy, os.R_OK):
            self.skipTest('File permissions are not enforced')
        self.check_config(self.legacy, proxy=None)

    def test_lookup_errors_keep_legacy(self):
        self.write_config(self.xdg)
        stat = os.stat

        for code in (errno.EACCES, errno.ELOOP, errno.ENOTDIR, errno.EIO):
            def lookup(path, *args, **kwargs):
                if path == str(self.legacy):
                    raise OSError(code, os.strerror(code), path)
                return stat(path, *args, **kwargs)

            with self.subTest(errno=code), patch.object(self.installer.os, 'stat', lookup):
                self.check_config(self.legacy, proxy=None)

    @unittest.skipIf(os.name == 'nt', 'Unix symlink fixture')
    def test_legacy_symlink_precedes_xdg(self):
        target = self.root / 'linked config'
        self.write_config(target)
        self.legacy.symlink_to(target)
        self.write_config(self.xdg, 'xdg.example:8080')
        self.check_config(self.legacy)

    @unittest.skipIf(os.name == 'nt', 'Unix symlink fixture')
    def test_dangling_legacy_symlink_uses_xdg(self):
        target = self.root / 'missing config'
        self.legacy.symlink_to(target)
        self.write_config(self.xdg)
        self.check_config(self.xdg)
        self.assertTrue(self.legacy.is_symlink())
        self.assertFalse(target.exists())

    @unittest.skipIf(os.name == 'nt', 'Unix symlink fixture')
    def test_legacy_symlink_loop_precedes_xdg(self):
        self.legacy.symlink_to(self.legacy.name)
        self.write_config(self.xdg)
        self.check_config(self.legacy, proxy=None)
        self.assertEqual(os.readlink(self.legacy), self.legacy.name)

    def test_argv_home_still_discovers_xdg(self):
        os.environ['HOME'] = os.environ['USERPROFILE'] = str(self.root / 'other home')
        sys.argv.append(str(self.home))
        self.write_config(self.default_xdg)
        del os.environ['XDG_CONFIG_HOME']
        self.check_config(self.default_xdg)

    def test_discovery_does_not_create_files(self):
        self.check_config(self.xdg, proxy=None)
        self.assertFalse(self.legacy.exists())
        self.assertFalse(self.xdg_home.exists())
        self.assertFalse((self.home / '.wakatime').exists())

    def test_resources_and_internal_config_stay_in_home(self):
        self.write_config(self.xdg)
        self.assertEqual(self.installer.getResourcesFolder(), str(self.home / '.wakatime'))
        self.assertEqual(
            self.installer.getConfigFile(True),
            str(self.home / '.wakatime' / 'wakatime-internal.cfg'),
        )
        self.assertEqual(Path(self.installer.getCliLocation()).parent, self.home / '.wakatime')

    def check_install(self, config, *, updating=False):
        proxy = 'selected-proxy.example:8080'
        self.write_config(config, proxy)
        contents = config.read_bytes()
        cli = Path(self.installer.getCliLocation())
        if updating:
            cli.parent.mkdir()
            cli.write_bytes(b'old cli')
            Path(self.installer.getSymlinkLocation()).write_bytes(b'old cli')

        archive = io.BytesIO()
        new_cli = b'new cli archive fixture\n'
        with ZipFile(archive, 'w') as zf:
            zf.writestr(cli.name, new_cli)
        architecture = self.installer.architecture()
        download_url = self.installer.cliDownloadUrl()
        release_url = self.installer.GITHUB_RELEASES_STABLE_URL
        requests = []

        def urlopen(request):
            url = request.get_full_url()
            requests.append((url, request.host))
            if request.host != proxy:
                raise IOError('Configured proxy required')
            if url == release_url:
                body = b'{"tag_name": "v2.28.0"}'
            else:
                self.assertEqual(url, download_url)
                body = archive.getvalue()
            response = Mock()
            response.read.return_value = body
            response.getheaders.return_value = []
            response.getcode.return_value = 200
            return response

        with patch.object(self.installer, 'urlopen', urlopen), \
                patch.object(self.installer, 'architecture', return_value=architecture), \
                patch.object(self.installer, 'Popen') as popen:
            popen.return_value.communicate.return_value = (b'wakatime-cli v2.27.13', b'')
            # Both editors pass their resource home to main, including for XDG setups.
            self.installer.main(home=str(self.home))

        expected = [release_url, download_url] if updating else [download_url]
        self.assertEqual(requests, [(url, proxy) for url in expected])
        self.assertEqual(cli.read_bytes(), new_cli)
        self.assertEqual(Path(self.installer.getSymlinkLocation()).read_bytes(), new_cli)
        self.assertEqual(config.read_bytes(), contents)
        self.assertEqual(self.installer.CONFIGS.get('settings', 'proxy'), proxy)
        if config != self.legacy:
            self.assertFalse(self.legacy.exists())
        if updating:
            internal = self.installer.parseConfigFile(self.installer.getConfigFile(True))
            self.assertEqual(internal.get('internal', 'cli_version'), 'v2.28.0')

    def test_first_install_uses_custom_xdg_proxy(self):
        self.check_install(self.xdg)

    def test_first_install_uses_default_xdg_proxy(self):
        del os.environ['XDG_CONFIG_HOME']
        self.check_install(self.default_xdg)

    def test_update_uses_custom_xdg_proxy(self):
        self.check_install(self.xdg, updating=True)

    def test_update_uses_default_xdg_proxy(self):
        del os.environ['XDG_CONFIG_HOME']
        self.check_install(self.default_xdg, updating=True)

    def check_cygwin_install(self, *, updating=False):
        with patch.object(self.installer.platform, 'system', return_value='CYGWIN_NT-10.0'), \
                patch.object(sys, 'dont_write_bytecode', True):
            self.installer.__spec__.loader.exec_module(self.installer)
            self.assertTrue(self.installer.is_win)
            self.assertEqual(self.installer.os.name, 'posix')
            self.assertIn('/wakatime-cli-windows-', self.installer.cliDownloadUrl())
            self.assertTrue(self.installer.getCliLocation().endswith('.exe'))
            self.check_install(self.xdg, updating=updating)
            self.assertEqual(self.installer.getConfigFile(), str(self.xdg))

    @unittest.skipUnless(os.name == 'posix', 'POSIX filesystem fixture')
    def test_cygwin_first_install_uses_custom_xdg_proxy(self):
        self.check_cygwin_install()

    @unittest.skipUnless(os.name == 'posix', 'POSIX filesystem fixture')
    def test_cygwin_update_uses_custom_xdg_proxy(self):
        self.check_cygwin_install(updating=True)

    def test_legacy_proxy_precedes_xdg_during_install(self):
        self.write_config(self.xdg, 'unselected-proxy.example:8080')
        self.check_install(self.legacy)

    def test_wakatime_home_proxy_precedes_xdg_during_update(self):
        os.environ['WAKATIME_HOME'] = str(self.home)
        self.write_config(self.xdg, 'unselected-proxy.example:8080')
        self.check_install(self.legacy, updating=True)


if __name__ == '__main__':
    unittest.main()
