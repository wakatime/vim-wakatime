"""Legacy config lookup fixture; optionally forward calls to an actual CLI."""

import configparser
import json
import os
from pathlib import Path
import subprocess
import sys


args = sys.argv[1:]
real_cli = os.environ.get('WAKATIME_TEST_REAL_CLI')
if real_cli:
    stdin = sys.stdin.readline() if '--extra-heartbeats' in args else None
    result = subprocess.run([real_cli, *args], input=stdin, capture_output=True, text=True, timeout=10)
    code, output, errors = result.returncode, result.stdout, result.stderr
else:
    config = Path(os.environ['HOME']) / '.wakatime.cfg'
    if '--config' in args:
        config = Path(args[args.index('--config') + 1])
    settings = configparser.ConfigParser()
    settings.read(config, encoding='utf-8')
    code = 0 if '--version' in args or settings.get('settings', 'api_key', fallback='') else 104
    output = 'v2.27.13\n' if '--version' in args else '0 mins\n' if '--today' in args else ''
    errors = ''

with open(os.environ['WAKATIME_TEST_CALL_LOG'], 'a', encoding='utf-8') as log:
    log.write(json.dumps({'args': args, 'code': code}) + '\n')
sys.stdout.write(output)
sys.stderr.write(errors)
sys.exit(code)
