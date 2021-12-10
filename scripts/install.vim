let s:home = expand("$WAKATIME_HOME")
if s:home == '$WAKATIME_HOME'
    let s:home = expand("$HOME")
endif

let s:plugin_root_folder = substitute(expand("<sfile>:p:h:h"), '\', '/', 'g')

if has('python3')
    python3 << EOF
import sys
import vim
from os.path import abspath, join
sys.path.insert(0, abspath(join(vim.eval('s:plugin_root_folder'), 'scripts')))
from install_cli import main
main(home=vim.eval('s:home'))
EOF
elseif has('python')
    python << EOF
import sys
import vim
from os.path import abspath, join
sys.path.insert(0, abspath(join(vim.eval('s:plugin_root_folder'), 'scripts')))
from install_cli import main
main(home=vim.eval('s:home'))
EOF
endif
