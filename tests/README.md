# Tests

Run the config discovery regressions from the repository root:

```sh
python3 tests/config_discovery.py
```

The suite starts a fresh Vim and Neovim process for each case, using temporary
home directories. Missing editors are skipped. To select particular executables:

```sh
WAKATIME_TEST_VIM=/usr/bin/vim WAKATIME_TEST_NVIM=/path/to/nvim python3 tests/config_discovery.py
```

It checks config precedence, reading and writing settings, missing directories,
directory search permission errors, and preservation of other configs and runtime
paths. Discovery cases use Python as a substitute CLI. Command cases use a
recording fixture to check that API-key writes and every runtime command use the
same config path, including paths with spaces and CLI executables found in PATH.
It also covers config paths containing `!`, cyclic legacy/XDG symlinks, and
restoration of Vim options after loading the plugin.
The default suite neither downloads WakaTime CLI nor contacts the WakaTime API.

For integration runs, the recording fixture can forward commands to
WAKATIME_TEST_REAL_CLI. Point WAKATIME_TEST_API_URL at a local WakaTime API stub
when using an actual CLI.

Run the Python installer's regressions separately:

```sh
python3 tests/install_cli.py
```

These check the same config precedence, including legacy file lookup errors,
and run initial installation and updates with proxy settings from default and
custom XDG configs. GitHub responses are replaced with in-memory release metadata
and CLI archives. The tests check the proxy on each release-check and download
request, extracted CLI files, and preservation of config and resource paths.
They do not access the network or require an installed CLI.

Native Windows path cases use `ntpath` and simulate Python 3.12's treatment of a
single leading separator as absolute. They check fallback for root-relative and
drive-relative XDG paths and acceptance of drive-rooted and UNC paths. These
portable checks do not run a Windows editor or perform a Windows installation.

Cygwin cases run initial installation and updates on a POSIX filesystem with
simulated Cygwin platform metadata. They check custom XDG proxy routing and
preservation of Windows download URLs and `.exe` executable names.
