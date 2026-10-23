"""Run with python3 tests/config_discovery.py; see README.md for editor overrides."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


PROBE = Path(__file__).with_suffix('.vim').resolve()
CONFIG = '[settings]\napi_key = config-file-key\nvi_redraw = disabled\n'


class ConfigDiscoveryCases:
    def setUp(self):
        self.editor = shutil.which(os.environ.get(self.editor_env, self.editor_name))
        if not self.editor:
            self.skipTest(f'{self.editor_name} is not installed')
        self.temp = tempfile.TemporaryDirectory(prefix='wakatime-config-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.home = self.root / 'home with spaces'
        self.home.mkdir()
        self.legacy = self.home / '.wakatime.cfg'
        self.xdg_home = self.root / 'xdg with spaces'
        self.xdg = self.xdg_home / 'wakatime' / 'wakatime.cfg'
        self.default_xdg = self.home / '.config' / 'wakatime' / 'wakatime.cfg'
        self.cli = Path(sys.executable).resolve()
        self.env = dict(os.environ)
        self.env.pop('WAKATIME_HOME', None)
        self.env.pop('XDG_CONFIG_HOME', None)
        self.env.update(
            HOME=str(self.home),
            USERPROFILE=str(self.home),
            WAKATIME_API_KEY='test-environment-key',
            WAKATIME_TEST_CLI=str(self.cli),
            WAKATIME_TEST_OUTPUT=str(self.root / 'state.json'),
            WAKATIME_TEST_ERROR=str(self.root / 'error.txt'),
            WAKATIME_TEST_REMOVE_DIR='',
            WAKATIME_TEST_RUN_CLI='',
        )

    def write_config(self, path, content=CONFIG):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')

    def check_config(self, expected, *, home=None, redraw='auto', write=True, setup=True):
        candidates = {self.legacy, self.xdg, self.default_xdg, expected}
        before = {
            path: path.read_bytes() if os.access(path, os.R_OK) and path.is_file() else None
            for path in candidates
        }
        self.env['WAKATIME_TEST_WRITE'] = '1' if write else '0'
        self.env['WAKATIME_TEST_SETUP'] = '1' if setup else '0'
        self.env['WAKATIME_TEST_CONFIG'] = str(expected)
        result = subprocess.run(
            [self.editor, '-Nu', 'NONE', '-i', 'NONE', '-n', '-es', '-S', str(PROBE)],
            cwd=self.root,
            env=self.env,
            capture_output=True,
            text=True,
            timeout=20,
        )
        error_file = Path(self.env['WAKATIME_TEST_ERROR'])
        errors = error_file.read_text(encoding='utf-8') if error_file.exists() else ''
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr + errors)
        state = json.loads(Path(self.env['WAKATIME_TEST_OUTPUT']).read_text(encoding='utf-8'))
        self.assertEqual(Path(state['config_file']), expected)
        self.assertEqual(Path(state['home']), home or self.home)
        self.assertEqual(Path(state['shared_state_file']), (home or self.home) / '.wakatime' / 'vim_shared_state')
        self.assertEqual(Path(state['cli']), self.cli)
        self.assertEqual(state['redraw_setting'], redraw)
        if write:
            self.assertIn('vi_redraw=enabled', expected.read_text(encoding='utf-8'))
        for path in candidates - {expected}:
            if before[path] is None:
                self.assertFalse(os.path.exists(path), f'Unexpected config created: {path}')
            else:
                self.assertEqual(path.read_bytes(), before[path], f'Other config changed: {path}')

    def test_existing_xdg(self):
        self.env['XDG_CONFIG_HOME'] = str(self.xdg_home)
        self.write_config(self.xdg)
        self.check_config(self.xdg, redraw='disabled')

    def test_existing_default_xdg(self):
        self.write_config(self.default_xdg)
        self.check_config(self.default_xdg, redraw='disabled')

    def check_cli_commands(self, config, *, global_cli=False):
        fixture = self.root / 'bin with spaces' / 'wakatime-cli'
        fixture.parent.mkdir()
        source = Path(__file__).with_name('cli_stub.py').read_text(encoding='utf-8')
        fixture.write_text(f'#!{sys.executable}\n' + source, encoding='utf-8')
        fixture.chmod(0o700)
        self.cli = Path('wakatime-cli') if global_cli else fixture
        self.env.pop('WAKATIME_API_KEY', None)
        api_url = self.env.get('WAKATIME_TEST_API_URL', 'http://127.0.0.1:9')
        self.write_config(
            config,
            '[settings]\nstatus_bar_enabled = false\nvi_redraw = disabled\n'
            f'api_url = {api_url}\n',
        )
        sample = self.root / 'sample file.txt'
        sample.write_text('test\n', encoding='utf-8')
        key = '00000000-0000-4000-8000-000000000001'
        log = self.root / 'cli-calls.jsonl'
        self.env.update(
            WAKATIME_TEST_CLI='' if global_cli else str(fixture),
            WAKATIME_TEST_RUN_CLI='1',
            WAKATIME_TEST_API_KEY=key,
            WAKATIME_TEST_CALL_LOG=str(log),
            WAKATIME_TEST_SAMPLE=str(sample),
            PATH=str(fixture.parent) + os.pathsep + self.env.get('PATH', ''),
        )
        self.check_config(config, redraw='disabled')
        calls = [json.loads(line) for line in log.read_text(encoding='utf-8').splitlines()]
        expected_flags = ['--today', '--file-experts', '--version', '--entity']
        if self.editor_name == 'nvim':
            expected_flags.append('--today')  # Statusline refresh.
        self.assertEqual(len(calls), len(expected_flags), calls)
        for call, flag in zip(calls, expected_flags):
            self.assertIn(flag, call['args'])
            self.assertEqual(call['args'].count('--config'), 1, call)
            index = call['args'].index('--config')
            self.assertEqual(call['args'][index + 1], str(config), call)
            self.assertEqual(call['code'], 0, call)
        self.assertIn('api_key=' + key, config.read_text(encoding='utf-8'))

    @unittest.skipIf(os.name == 'nt', 'Unix executable fixture')
    def test_cli_commands_use_default_xdg(self):
        self.check_cli_commands(self.default_xdg)

    @unittest.skipIf(os.name == 'nt', 'Unix executable fixture')
    def test_cli_commands_use_custom_xdg(self):
        self.env['XDG_CONFIG_HOME'] = str(self.xdg_home)
        self.check_cli_commands(self.xdg)

    @unittest.skipIf(os.name == 'nt', 'Unix executable fixture')
    def test_cli_commands_use_global_cli(self):
        self.env['XDG_CONFIG_HOME'] = str(self.xdg_home)
        self.check_cli_commands(self.xdg, global_cli=True)

    @unittest.skipIf(os.name == 'nt', 'Unix executable fixture')
    def test_cli_commands_use_legacy_config(self):
        self.env['XDG_CONFIG_HOME'] = str(self.xdg_home)
        self.check_cli_commands(self.legacy)

    @unittest.skipIf(os.name == 'nt', 'Unix executable fixture')
    def test_cli_commands_use_legacy_config_with_bang_in_home(self):
        self.home = self.root / 'home! with spaces'
        self.home.mkdir()
        self.legacy = self.home / '.wakatime.cfg'
        self.default_xdg = self.home / '.config' / 'wakatime' / 'wakatime.cfg'
        self.env.update(HOME=str(self.home), USERPROFILE=str(self.home))
        self.check_cli_commands(self.legacy)

    @unittest.skipIf(os.name == 'nt', 'Unix executable fixture')
    def test_cli_commands_use_custom_xdg_with_bang(self):
        self.xdg_home = self.root / 'xdg! with spaces'
        self.xdg = self.xdg_home / 'wakatime' / 'wakatime.cfg'
        self.env['XDG_CONFIG_HOME'] = str(self.xdg_home)
        self.check_cli_commands(self.xdg)

    @unittest.skipIf(os.name == 'nt', 'Unix executable symlink fixture')
    def test_xdg_keeps_managed_cli_in_home(self):
        if any(shutil.which(name, path=os.defpath) for name in ('wakatime-cli', 'wakatime')):
            self.skipTest('A system CLI takes precedence over the managed fixture')
        executable = self.cli
        self.cli = self.home / '.wakatime' / 'wakatime-cli'
        self.cli.parent.mkdir()
        self.cli.symlink_to(executable)
        self.env.update(
            XDG_CONFIG_HOME=str(self.xdg_home),
            WAKATIME_TEST_CLI='',
            PATH=os.defpath,
        )
        self.write_config(self.xdg)
        self.check_config(self.xdg, redraw='disabled')

    def test_legacy_precedes_xdg(self):
        self.env['XDG_CONFIG_HOME'] = str(self.xdg_home)
        self.write_config(self.legacy)
        self.write_config(self.xdg, CONFIG.replace('disabled', 'enabled'))
        self.check_config(self.legacy, redraw='disabled')

    def test_empty_legacy_precedes_xdg(self):
        self.env['XDG_CONFIG_HOME'] = str(self.xdg_home)
        self.write_config(self.legacy, '')
        self.write_config(self.xdg)
        self.check_config(self.legacy)

    @unittest.skipIf(os.name == 'nt', 'Unix symlink fixture')
    def test_legacy_symlink_precedes_xdg(self):
        target = self.root / 'linked-config'
        self.write_config(target)
        self.legacy.symlink_to(target)
        self.env['XDG_CONFIG_HOME'] = str(self.xdg_home)
        self.write_config(self.xdg)
        self.check_config(self.legacy, redraw='disabled')
        self.assertTrue(self.legacy.is_symlink())
        self.assertIn('vi_redraw=enabled', target.read_text(encoding='utf-8'))

    @unittest.skipIf(os.name == 'nt', 'Unix symlink fixture')
    def test_dangling_legacy_symlink_uses_xdg(self):
        target = self.root / 'missing-linked-config'
        self.legacy.symlink_to(target)
        self.env['XDG_CONFIG_HOME'] = str(self.xdg_home)
        self.write_config(self.xdg)
        self.check_config(self.xdg, redraw='disabled')
        self.assertTrue(self.legacy.is_symlink())
        self.assertFalse(target.exists())

    @unittest.skipIf(os.name == 'nt', 'Unix symlink fixture')
    def test_legacy_symlink_loop_keeps_legacy(self):
        self.env['XDG_CONFIG_HOME'] = str(self.xdg_home)
        self.write_config(self.xdg)
        self.legacy.symlink_to(self.legacy.name)
        self.check_config(self.legacy, write=False)
        self.assertEqual(os.readlink(self.legacy), self.legacy.name)

    @unittest.skipIf(os.name == 'nt', 'Unix symlink fixture')
    def test_legacy_two_link_cycle_keeps_legacy(self):
        self.env['XDG_CONFIG_HOME'] = str(self.xdg_home)
        self.write_config(self.xdg)
        target = self.root / 'loop target'
        self.legacy.symlink_to(target)
        target.symlink_to(self.legacy)
        self.check_config(self.legacy, write=False)
        self.assertEqual(os.readlink(self.legacy), str(target))
        self.assertEqual(os.readlink(target), str(self.legacy))

    @unittest.skipIf(os.name == 'nt', 'Unix symlink fixture')
    def test_xdg_symlink_loop_is_not_recreated(self):
        self.env['XDG_CONFIG_HOME'] = str(self.xdg_home)
        self.xdg.parent.mkdir(parents=True)
        self.xdg.symlink_to(self.xdg.name)
        self.check_config(self.xdg, write=False)
        self.assertEqual(os.readlink(self.xdg), self.xdg.name)

    @unittest.skipIf(os.name == 'nt', 'Unix file permissions')
    def test_unreadable_legacy_precedes_xdg(self):
        self.env['XDG_CONFIG_HOME'] = str(self.xdg_home)
        self.write_config(self.legacy)
        self.write_config(self.xdg)
        self.legacy.chmod(0)
        self.addCleanup(self.legacy.chmod, 0o600)
        if os.access(self.legacy, os.R_OK):
            self.skipTest('File permissions are not enforced')
        self.check_config(self.legacy, write=False)
        self.legacy.chmod(0o600)
        self.assertEqual(self.legacy.read_text(encoding='utf-8'), CONFIG)

    def check_unsearchable_directory(self, directory, mode=0):
        original_mode = directory.stat().st_mode & 0o777
        directory.chmod(mode)
        try:
            try:
                self.legacy.stat()
            except PermissionError:
                pass
            else:
                self.skipTest('Directory search permissions are not enforced')
            self.check_config(self.legacy, write=False)
        finally:
            directory.chmod(original_mode)
        self.assertEqual(self.legacy.read_text(encoding='utf-8'), CONFIG)
        self.assertEqual(self.xdg.read_text(encoding='utf-8'), CONFIG)
        self.assertFalse(self.default_xdg.exists())

    @unittest.skipIf(os.name == 'nt', 'Unix directory permissions')
    def test_unsearchable_home_keeps_legacy(self):
        self.env['XDG_CONFIG_HOME'] = str(self.xdg_home)
        self.write_config(self.legacy)
        self.write_config(self.xdg)
        self.check_unsearchable_directory(self.home)

    @unittest.skipIf(os.name == 'nt', 'Unix directory permissions')
    def test_readable_unsearchable_home_keeps_legacy(self):
        self.env['XDG_CONFIG_HOME'] = str(self.xdg_home)
        self.write_config(self.legacy)
        self.write_config(self.xdg)
        self.check_unsearchable_directory(self.home, mode=0o400)

    @unittest.skipIf(os.name == 'nt', 'Unix directory permissions')
    def test_unsearchable_ancestor_keeps_legacy(self):
        ancestor = self.home
        self.home = ancestor / 'nested-home'
        self.home.mkdir()
        self.legacy = self.home / '.wakatime.cfg'
        self.default_xdg = self.home / '.config' / 'wakatime' / 'wakatime.cfg'
        self.env.update(HOME=str(self.home), USERPROFILE=str(self.home), XDG_CONFIG_HOME=str(self.xdg_home))
        self.write_config(self.legacy)
        self.write_config(self.xdg)
        self.check_unsearchable_directory(ancestor)

    @unittest.skipIf(os.name == 'nt', 'Unix symlink fixture and directory permissions')
    def test_unsearchable_symlink_target_keeps_legacy(self):
        target = self.root / 'private-config' / 'wakatime.cfg'
        self.write_config(target)
        self.legacy.symlink_to(target)
        self.env['XDG_CONFIG_HOME'] = str(self.xdg_home)
        self.write_config(self.xdg)
        self.check_unsearchable_directory(target.parent)
        self.assertTrue(self.legacy.is_symlink())

    @unittest.skipIf(os.name == 'nt', 'Unix directory permissions')
    def test_unreadable_searchable_home_uses_xdg(self):
        self.env['XDG_CONFIG_HOME'] = str(self.xdg_home)
        self.write_config(self.xdg)
        self.home.chmod(0o100)
        try:
            with self.assertRaises(FileNotFoundError):
                self.legacy.stat()
            self.check_config(self.xdg, redraw='disabled')
        finally:
            self.home.chmod(0o700)

    def test_missing_home_uses_xdg(self):
        self.home.rmdir()
        self.env['XDG_CONFIG_HOME'] = str(self.xdg_home)
        self.write_config(self.xdg)
        self.check_config(self.xdg, redraw='disabled')

    def test_wakatime_home_precedes_both_configs(self):
        override = self.root / 'override with spaces'
        config = override / '.wakatime.cfg'
        self.env.update(WAKATIME_HOME=str(override), XDG_CONFIG_HOME=str(self.xdg_home))
        self.write_config(config)
        self.write_config(self.legacy, CONFIG.replace('disabled', 'enabled'))
        self.write_config(self.xdg, CONFIG.replace('disabled', 'enabled'))
        self.check_config(config, home=override, redraw='disabled')

    def test_missing_wakatime_home_config(self):
        override = self.root / 'missing override'
        self.env.update(WAKATIME_HOME=str(override), XDG_CONFIG_HOME=str(self.xdg_home))
        self.write_config(self.legacy)
        self.write_config(self.xdg)
        self.check_config(override / '.wakatime.cfg', home=override)

    def test_tilde_wakatime_home(self):
        self.env['WAKATIME_HOME'] = '~/override'
        override = self.home / 'override'
        self.check_config(override / '.wakatime.cfg', home=override)

    def test_empty_wakatime_home_uses_xdg(self):
        self.env.update(WAKATIME_HOME='', XDG_CONFIG_HOME=str(self.xdg_home))
        self.write_config(self.xdg)
        self.check_config(self.xdg, redraw='disabled')

    def test_empty_wakatime_home_keeps_legacy(self):
        self.env.update(WAKATIME_HOME='', XDG_CONFIG_HOME=str(self.xdg_home))
        self.write_config(self.legacy)
        self.write_config(self.xdg)
        self.check_config(self.legacy, redraw='disabled')

    def test_create_custom_xdg_parents(self):
        self.env['XDG_CONFIG_HOME'] = str(self.xdg_home)
        self.check_config(self.xdg)
        if os.name != 'nt':
            self.assertEqual(self.xdg.parent.stat().st_mode & 0o777, 0o700)

    def test_create_default_xdg_parents(self):
        self.check_config(self.default_xdg)

    def test_command_before_first_activity(self):
        self.env['XDG_CONFIG_HOME'] = str(self.xdg_home)
        self.check_config(self.xdg, setup=False)

    def test_command_recreates_config_directory(self):
        self.env['XDG_CONFIG_HOME'] = str(self.xdg_home)
        self.env['WAKATIME_TEST_REMOVE_DIR'] = str(self.xdg.parent)
        self.check_config(self.xdg, setup=False)
        if os.name != 'nt':
            self.assertEqual(self.xdg.parent.stat().st_mode & 0o777, 0o700)

    @unittest.skipIf(os.name == 'nt', 'Unix file permissions')
    def test_existing_directory_permissions_unchanged(self):
        self.env['XDG_CONFIG_HOME'] = str(self.xdg_home)
        self.xdg.parent.mkdir(parents=True)
        self.xdg.parent.chmod(0o750)
        self.check_config(self.xdg)
        self.assertEqual(self.xdg.parent.stat().st_mode & 0o777, 0o750)

    def test_empty_xdg_uses_default(self):
        self.env['XDG_CONFIG_HOME'] = ''
        self.check_config(self.default_xdg)

    def test_relative_xdg_uses_default(self):
        self.env['XDG_CONFIG_HOME'] = 'relative-config'
        self.check_config(self.default_xdg)
        self.assertFalse((self.root / 'relative-config').exists())

    def test_tilde_xdg_uses_default(self):
        self.env['XDG_CONFIG_HOME'] = '~/custom-config'
        self.check_config(self.default_xdg)
        self.assertFalse((self.home / 'custom-config').exists())

    def test_absolute_xdg_is_not_expanded(self):
        self.xdg_home = self.root / '$HOME' / 'literal-config'
        self.xdg = self.xdg_home / 'wakatime' / 'wakatime.cfg'
        self.env['XDG_CONFIG_HOME'] = str(self.xdg_home)
        self.check_config(self.xdg)


class VimConfigDiscovery(ConfigDiscoveryCases, unittest.TestCase):
    editor_env = 'WAKATIME_TEST_VIM'
    editor_name = 'vim'


class NeovimConfigDiscovery(ConfigDiscoveryCases, unittest.TestCase):
    editor_env = 'WAKATIME_TEST_NVIM'
    editor_name = 'nvim'


if __name__ == '__main__':
    unittest.main()
