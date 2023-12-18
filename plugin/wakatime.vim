" ============================================================================
" File:        wakatime.vim
" Description: Automatic time tracking for Vim.
" Maintainer:  WakaTime <support@wakatime.com>
" License:     BSD, see LICENSE.txt for more details.
" Website:     https://wakatime.com/
" ============================================================================

let s:VERSION = '11.1.1'


" Init {{{

    " Check Vim version
    if v:version < 700
        echoerr "The WakaTime plugin requires vim >= 7."
        finish
    endif

    " Use constants to improve readability
    let s:true = 1
    let s:false = 0
    let s:exit_code_config_parse_error = 103
    let s:exit_code_api_key_error = 104

    " Only load plugin once
    if exists("g:loaded_wakatime")
        finish
    endif
    let g:loaded_wakatime = s:true

    " Backup & Override cpoptions
    let s:old_cpo = &cpo
    set cpo&vim

    " Backup wildignore before clearing it to prevent conflicts with expand()
    let s:wildignore = &wildignore
    if s:wildignore != ""
        set wildignore=""
    endif

    " Script Globals
    let s:home = ''
    if exists('$WAKATIME_HOME')
        let s:home = expand(expand('$WAKATIME_HOME'))
    else
        let s:home = expand(expand("$HOME"))
    endif
    let s:home = substitute(s:home, '\', '/', 'g')
    let s:plugin_root_folder = substitute(expand("<sfile>:p:h:h"), '\', '/', 'g')
    let s:config_file = s:home . '/.wakatime.cfg'
    let s:default_configs = ['[settings]', 'debug = false', 'hidefilenames = false', 'ignore =', '    COMMIT_EDITMSG$', '    PULLREQ_EDITMSG$', '    MERGE_MSG$', '    TAG_EDITMSG$']
    let s:shared_state_parent_dir = s:home . '/.wakatime'
    let s:shared_state_file = s:shared_state_parent_dir . '/vim_shared_state'
    let s:has_reltime = has('reltime') && localtime() - 1 < split(split(reltimestr(reltime()))[0], '\.')[0]
    let s:config_file_already_setup = s:false
    let s:debug_mode_already_setup = s:false
    let s:cli_already_setup = s:false
    let s:is_debug_on = s:false
    let s:local_cache_expire = 10  " seconds between reading s:shared_state_file
    let s:last_heartbeat = {'last_activity_at': 0, 'last_heartbeat_at': 0, 'file': ''}
    let s:heartbeats_buffer = []
    let s:send_buffer_seconds = 30  " seconds between sending buffered heartbeats
    let s:last_sent = localtime()
    let s:has_async_patch = has('patch-7.4-2344') || v:version >= 800
    let s:has_async = s:has_async_patch && exists('*job_start')
    let s:nvim_async = exists('*jobstart')

    function! s:Init()
        " Set default heartbeat frequency in minutes
        if !exists("g:wakatime_HeartbeatFrequency")
            let g:wakatime_HeartbeatFrequency = 2
        endif

        " Get legacy g:wakatime_ScreenRedraw setting
        let s:redraw_setting = 'auto'
        if exists("g:wakatime_ScreenRedraw") && g:wakatime_ScreenRedraw
            let s:redraw_setting = 'enabled'
        endif

        " Get redraw setting from wakatime.cfg file
        let vi_redraw = s:GetIniSetting('settings', 'vi_redraw')
        if !empty(vi_redraw)
            if vi_redraw == 'enabled'
                let s:redraw_setting = 'enabled'
            endif
            if vi_redraw == 'auto'
                let s:redraw_setting = 'auto'
            endif
            if vi_redraw == 'disabled'
                let s:redraw_setting = 'disabled'
            endif
        endif

        " Buffering heartbeats disabled in Windows, unless have async support
        let s:buffering_heartbeats_enabled = s:has_async || s:nvim_async || !s:IsWindows()

        " Turn on autoupdate only when using default ~/.wakatime/wakatime-cli
        let s:autoupdate_cli = s:false

        " Check vimrc config for wakatime-cli binary path
        if exists("g:wakatime_CLIPath") && filereadable(g:wakatime_CLIPath)
            let s:wakatime_cli = g:wakatime_CLIPath

        " Legacy configuration of wakatime-cli
        elseif exists("g:wakatime_OverrideCommandPrefix") && filereadable(g:wakatime_OverrideCommandPrefix)
            let s:wakatime_cli = g:wakatime_OverrideCommandPrefix

        " Check $PATH and ~/.wakatime/wakatime-cli symlink
        else
            let path = s:home . '/.wakatime/wakatime-cli'

            " Check for wakatime-cli
            if !filereadable(path) && s:Executable('wakatime-cli')
                let s:wakatime_cli = 'wakatime-cli'

            " Check for wakatime
            elseif !filereadable(path) && s:Executable('wakatime') && !s:Contains(exepath('wakatime'), 'npm') && !s:Contains(exepath('wakatime'), 'node')
                let s:wakatime_cli = 'wakatime'

            " Check for wakatime-cli installed via Homebrew
            elseif !filereadable(path) && filereadable('/usr/local/bin/wakatime-cli')
                let s:wakatime_cli = '/usr/local/bin/wakatime-cli'

            " Default to ~/.wakatime/wakatime-cli
            else
                let s:autoupdate_cli = s:true
                let s:wakatime_cli = path
                if s:IsWindows()
                    let s:wakatime_cli = s:wakatime_cli . '.exe'
                endif
            endif
        endif

    endfunction

    function! s:InstallCLI(use_external_python)
        if !s:autoupdate_cli && s:Executable(s:wakatime_cli)
            return
        endif

        let python_bin = ''
        if a:use_external_python
            let python_bin = s:GetPythonBinary()
        endif

        " First try install wakatime-cli in background, then using Vim's Python
        if !empty(python_bin)
            let install_script = s:plugin_root_folder . '/scripts/install_cli.py'

            " Fix for Python installed with pacman on msys2 https://github.com/wakatime/vim-wakatime/issues/122
            " Turns Windows path into Unix-like path
            if s:IsWindows() && exepath(python_bin) =~ '[/\\]s\?bin[/\\]'
                let install_script = substitute(install_script, '^/\?\([a-zA-Z]\):/', '/\1/', '')
            endif

            let cmd = [python_bin, '-W', 'ignore', install_script, s:home]
            if s:has_async
                if !s:IsWindows()
                    let job_cmd = [&shell, &shellcmdflag, s:JoinArgs(cmd)]
                elseif &shell =~ 'sh\(\.exe\)\?$'
                    let job_cmd = [&shell, '-c', s:JoinArgs(cmd)]
                else
                    let job_cmd = [&shell, &shellcmdflag] + cmd
                endif
                let job = job_start(job_cmd, {
                    \ 'stoponexit': '',
                    \ 'callback': {channel, output -> s:AsyncInstallHandler(output)}})
            elseif s:nvim_async
                if s:IsWindows()
                    let job_cmd = cmd
                else
                    let job_cmd = [&shell, &shellcmdflag, s:JoinArgs(cmd)]
                endif
                let s:nvim_async_output = ['']
                let job_opts = {
                    \ 'on_stdout': function('s:NeovimAsyncInstallOutputHandler'),
                    \ 'on_stderr': function('s:NeovimAsyncInstallOutputHandler'),
                    \ 'on_exit': function('s:NeovimAsyncInstallExitHandler')}
                if !s:IsWindows()
                    let job_opts['detach'] = 1
                endif
                let job = jobstart(job_cmd, job_opts)
            elseif s:IsWindows()
                if s:is_debug_on
                    let stdout = s:StripWhitespace(system('(' . s:JoinArgs(cmd) . ')'))
                    if !empty(stdout) && !s:Contains(stdout, 'wakatime-cli is up to date')
                        echo printf("[WakaTime] error installing wakatime-cli for Windows:\n%s\n[WakaTime] Will retry using Vim built-in Python.", stdout)
                        call s:InstallCLI(s:false)
                    endif
                else
                    exec 'silent !start /b cmd /c "' . s:JoinArgs(cmd) . ' > nul 2> nul"'
                endif
            else
                if s:is_debug_on
                    let stdout = s:StripWhitespace(system(s:JoinArgs(cmd)))
                    if !empty(stdout) && !s:Containsstridx(stdout, 'wakatime-cli is up to date')
                        echo printf("[WakaTime] error installing wakatime-cli:\n%s\n[WakaTime] Will retry using Vim built-in Python.", stdout)
                        call s:InstallCLI(s:false)
                    endif
                else
                    let stdout = s:StripWhitespace(system(s:JoinArgs(cmd) . ' &'))
                    if !empty(stdout) && !s:Containsstridx(stdout, 'wakatime-cli is up to date')
                        call s:InstallCLI(s:false)
                    endif
                endif
            endif
        elseif s:Executable(v:progname) && (has('python3') || has('python') || has('python3_dynamic') || has('python_dynamic'))
            call s:InstallCLIRoundAbout()
        elseif has('python3') || has('python3_dynamic')
            python3 << EOF
import sys
import vim
from os.path import abspath, join
sys.path.insert(0, abspath(join(vim.eval('s:plugin_root_folder'), 'scripts')))
from install_cli import main
main(home=vim.eval('s:home'))
EOF
        elseif has('python') || has('python_dynamic')
            python << EOF
import sys
import vim
from os.path import abspath, join
sys.path.insert(0, abspath(join(vim.eval('s:plugin_root_folder'), 'scripts')))
from install_cli import main
main(home=vim.eval('s:home'))
EOF
        elseif !filereadable(s:wakatime_cli)

            " use Powershell to install wakatime-cli because NeoVim doesn't
            " come installed with Python bundled (https://github.com/wakatime/vim-wakatime/issues/147)
            if s:IsWindows()
                echo "Downloading wakatime-cli to ~/.wakatime/... this may take a while but only needs to be done once..."

                let cmd = 'if ((Get-WmiObject win32_operatingsystem | select osarchitecture).osarchitecture -like "64*") { Write "amd64" } else { Write "386" }'
                let arch = s:Chomp(system(['powershell.exe', '-noprofile', '-command'] + [cmd]))

                let url = "https://github.com/wakatime/wakatime-cli/releases/latest/download/wakatime-cli-windows-" . arch . ".zip"
                let zipfile = s:home . "/.wakatime/wakatime-cli.zip"

                let cmd = 'Invoke-WebRequest -Uri ' . url . ' -OutFile ' . shellescape(zipfile)
                call system(['powershell.exe', '-noprofile', '-command'] + [cmd])

                let cmd = 'Add-Type -AssemblyName System.IO.Compression.FileSystem; [System.IO.Compression.ZipFile]::ExtractToDirectory(' . shellescape(zipfile) . ', ' . shellescape(s:home . '/.wakatime') . ')'
                call system(['powershell.exe', '-noprofile', '-command'] + [cmd])

                let cmd = 'Rename-Item -Path ' . shellescape(s:home . '/.wakatime/wakatime-cli-windows-amd64.exe') . ' -NewName ' . shellescape(s:home . '/.wakatime/wakatime-cli.exe')
                call system(['powershell.exe', '-noprofile', '-command'] + [cmd])

                call delete(fnameescape(zipfile))

                echo "Finished installing wakatime-cli."

            " last resort, ask to manually download wakatime-cli
            else
                let url = 'https://github.com/wakatime/wakatime-cli/releases'
                echo printf("Download wakatime-cli and extract into the ~/.wakatime/ folder:\n%s", url)
            endif
        endif
    endfunction

    function! s:InstallCLIRoundAbout()
        if has('python3') || has('python3_dynamic')
            let py = 'python3'
        else
            let py = 'python'
        endif
        let code = py . " import sys, vim;from os.path import abspath, join;sys.path.insert(0, abspath(join('" . s:plugin_root_folder . "', 'scripts')));from install_cli import main;main(home='" . s:home . "');"
        let cmd = [v:progname, '-u', 'NONE', '-c', code, '+qall']
        if s:has_async
            if !s:IsWindows()
                let job_cmd = [&shell, &shellcmdflag, s:JoinArgs(cmd)]
            elseif &shell =~ 'sh\(\.exe\)\?$'
                let job_cmd = [&shell, '-c', s:JoinArgs(cmd)]
            else
                let job_cmd = [&shell, &shellcmdflag] + cmd
            endif
            let job = job_start(job_cmd, {'stoponexit': ''})
        elseif s:nvim_async
            if s:IsWindows()
                let job_cmd = cmd
            else
                let job_cmd = [&shell, &shellcmdflag, s:JoinArgs(cmd)]
            endif
            let job_opts = {}
            if !s:IsWindows()
                let job_opts['detach'] = 1
            endif
            let job = jobstart(job_cmd, job_opts)
        elseif s:IsWindows()
            if s:is_debug_on
                let stdout = system('(' . s:JoinArgs(cmd) . ')')
            else
                exec 'silent !start /b cmd /c "' . s:JoinArgs(cmd) . ' > nul 2> nul"'
            endif
        else
            if s:is_debug_on
                let stdout = system(s:JoinArgs(cmd))
            else
                let stdout = system(s:JoinArgs(cmd) . ' &')
            endif
        endif
    endfunction

" }}}


" Function Definitions {{{

    function! s:StripWhitespace(str)
        return substitute(a:str, '^\s*\(.\{-}\)\s*$', '\1', '')
    endfunction

    function! s:Chomp(str)
        return substitute(a:str, '\n\+$', '', '')
    endfunction

    function! s:SetupConfigFile()
        if !s:config_file_already_setup

            " Create config file if does not exist
            if !filereadable(s:config_file)
                call writefile(s:default_configs, s:config_file)
            endif

            " Make sure config file has api_key
            let found_api_key = s:false
            if !empty(s:GetIniSetting('settings', 'api_key')) || !empty(s:GetIniSetting('settings', 'apikey'))
                let found_api_key = s:true
            endif

            if !found_api_key
                let vault_cmd = s:GetIniSetting('settings', 'api_key_vault_cmd')
                if !empty(vault_cmd) && !empty(s:Chomp(system(vault_cmd)))
                    let found_api_key = s:true
                endif
            endif

            if !found_api_key
                call s:PromptForApiKey()
                echo "[WakaTime] Setup complete! Visit https://wakatime.com to view your coding activity."
            endif

            let s:config_file_already_setup = s:true
        endif
    endfunction

    function! s:SetupCLI()
        if !s:cli_already_setup
            let s:cli_already_setup = s:true
            call s:InstallCLI(s:true)
        endif
    endfunction

    function! s:SetupDebugMode()
        if !s:debug_mode_already_setup
            if s:GetIniSetting('settings', 'debug') == 'true'
                let s:is_debug_on = s:true
            else
                let s:is_debug_on = s:false
            endif
            let s:debug_mode_already_setup = s:true
        endif
    endfunction

    function! s:GetIniSetting(section, key)
        if !filereadable(s:config_file)
            return ''
        endif
        let lines = readfile(s:config_file)
        let currentSection = ''
        for line in lines
            let line = s:StripWhitespace(line)
            if !empty(matchstr(line, '^\[')) && !empty(matchstr(line, '\]$'))
                let currentSection = substitute(line, '^\[\(.\{-}\)\]$', '\1', '')
            else
                if currentSection == a:section
                    let group = split(line, '=')
                    if len(group) == 2 && s:StripWhitespace(group[0]) == a:key
                        return s:StripWhitespace(group[1])
                    endif
                endif
            endif
        endfor
        return ''
    endfunction

    function! s:SetIniSetting(section, key, val)
        let output = []
        let sectionFound = s:false
        let keyFound = s:false
        if filereadable(s:config_file)
            let lines = readfile(s:config_file)
            let currentSection = ''
            for line in lines
                let entry = s:StripWhitespace(line)
                if !empty(matchstr(entry, '^\[')) && !empty(matchstr(entry, '\]$'))
                    if currentSection == a:section && !keyFound
                        let output = output + [join([a:key, a:val], '=')]
                        let keyFound = s:true
                    endif
                    let currentSection = substitute(entry, '^\[\(.\{-}\)\]$', '\1', '')
                    let output = output + [line]
                    if currentSection == a:section
                        let sectionFound = s:true
                    endif
                else
                    if currentSection == a:section
                        let group = split(entry, '=')
                        if len(group) == 2 && s:StripWhitespace(group[0]) == a:key
                            let output = output + [join([a:key, a:val], '=')]
                            let keyFound = s:true
                        else
                            let output = output + [line]
                        endif
                    else
                        let output = output + [line]
                    endif
                endif
            endfor
        endif
        if !sectionFound
            let output = output + [printf('[%s]', a:section), join([a:key, a:val], '=')]
        else
            if !keyFound
                let output = output + [join([a:key, a:val], '=')]
            endif
        endif
        call writefile(output, s:config_file)
    endfunction

    function! s:GetPythonBinary()
        let python_bin = ""
        if has('g:wakatime_PythonBinary')
            let python_bin = g:wakatime_PythonBinary
        endif
        if !s:Executable(python_bin) || !filereadable(python_bin)
            if s:Executable('python3')
                let python_bin = 'python3'
            elseif s:Executable('python')
                let python_bin = 'python'
            else
                let paths = ['python3']
                if s:IsWindows()
                    let pyver = 39
                    while pyver >= 27
                        let paths = paths + [printf('/Python%d/pythonw', pyver), printf('/python%d/pythonw', pyver), printf('/Python%d/python', pyver), printf('/python%d/python', pyver)]
                        let pyver = pyver - 1
                    endwhile
                else
                    let paths = paths + ['/usr/bin/python3', '/usr/local/bin/python3', '/usr/bin/python3.6', '/usr/local/bin/python3.6', '/usr/bin/python', '/usr/local/bin/python', '/usr/bin/python2', '/usr/local/bin/python2']
                endif
                let paths = paths + ['python']
                let index = 0
                let limit = len(paths)
                while index < limit
                    if filereadable(paths[index])
                        let python_bin = paths[index]
                        let index = limit
                    endif
                    let index = index + 1
                endwhile
            endif
        endif
        if s:IsWindows() && (filereadable(printf('%sw', python_bin)) || s:Executable(printf('%sw', python_bin)))
            let python_bin = printf('%sw', python_bin)
        endif
        return python_bin
    endfunction

    function! s:GetCurrentFile()
        return expand("%:p")
    endfunction

    function! s:SanitizeArg(arg)
        let sanitized = shellescape(a:arg)
        let sanitized = substitute(sanitized, '!', '\\!', 'g')
        return sanitized
    endfunction

    function! s:JsonEscape(str)
        return substitute(a:str, '"', '\\"', 'g')
    endfunction

    function! s:JoinArgs(args)
        let safeArgs = []
        for arg in a:args
            let safeArgs = safeArgs + [s:SanitizeArg(arg)]
        endfor
        return join(safeArgs, ' ')
    endfunction

    function! s:IsWindows()
        if has('win32')
            return s:true
        endif
        return s:false
    endfunction

    function! s:CurrentTimeStr()
        if s:has_reltime
            return split(reltimestr(reltime()))[0]
        endif
        return s:n2s(localtime())
    endfunction

    function! s:AppendHeartbeat(file, now, is_write, last)
        let file = a:file
        if empty(file)
            let file = a:last.file
        endif
        if !empty(file)
            let heartbeat = {}
            let heartbeat.entity = file
            let heartbeat.time = s:CurrentTimeStr()
            let heartbeat.is_write = a:is_write
            if !empty(&syntax) && &syntax != 'ON'
                let heartbeat.language = &syntax
            else
                if !empty(&filetype)
                    let heartbeat.language = &filetype
                endif
            endif
            let s:heartbeats_buffer = s:heartbeats_buffer + [heartbeat]
            call s:SetLastHeartbeat(a:now, a:now, file)

            if !s:buffering_heartbeats_enabled
                call s:SendHeartbeats()
            endif
        endif
    endfunction

    function! s:SendHeartbeats()
        let start_time = localtime()
        let stdout = ''

        if len(s:heartbeats_buffer) == 0
            let s:last_sent = start_time
            return
        endif

        let heartbeat = s:heartbeats_buffer[0]
        let s:heartbeats_buffer = s:heartbeats_buffer[1:-1]
        if len(s:heartbeats_buffer) > 0
            let extra_heartbeats = s:GetHeartbeatsJson()
        else
            let extra_heartbeats = ''
        endif

        let cmd = [s:wakatime_cli, '--entity', heartbeat.entity]
        let cmd = cmd + ['--time', heartbeat.time]

        let editor_name = 'vim'
        if has('nvim')
            let editor_name = 'neovim'
        endif
        let cmd = cmd + ['--plugin', printf('vim/%s %s-wakatime/%s', s:n2s(v:version), editor_name, s:VERSION)]

        if heartbeat.is_write
            let cmd = cmd + ['--write']
        endif
        if has_key(heartbeat, 'language')
            let cmd = cmd + ['--alternate-language', heartbeat.language]
        endif
        if !empty(extra_heartbeats)
            let cmd = cmd + ['--extra-heartbeats']
        endif

        " overwrite shell
        let [sh, shellcmdflag, shrd] = [&shell, &shellcmdflag, &shellredir]
        if !s:IsWindows()
            set shell=sh shellredir=>%s\ 2>&1
        endif

        if s:has_async
            if !s:IsWindows()
                let job_cmd = [&shell, &shellcmdflag, s:JoinArgs(cmd)]
            elseif &shell =~ 'sh\(\.exe\)\?$'
                let job_cmd = [&shell, '-c', s:JoinArgs(cmd)]
            else
                let job_cmd = [&shell, &shellcmdflag] + cmd
            endif
            let job = job_start(job_cmd, {
                \ 'stoponexit': '',
                \ 'callback': {channel, output -> s:AsyncHandler(output, cmd)}})
            if !empty(extra_heartbeats)
                let channel = job_getchannel(job)
                call ch_sendraw(channel, extra_heartbeats . "\n")
            endif
        elseif s:nvim_async
            if s:IsWindows()
                let job_cmd = cmd
            else
                let job_cmd = [&shell, &shellcmdflag, s:JoinArgs(cmd)]
            endif
            let s:nvim_async_output = ['']
            let job_opts = {
                \ 'on_stdout': function('s:NeovimAsyncOutputHandler'),
                \ 'on_stderr': function('s:NeovimAsyncOutputHandler'),
                \ 'on_exit': function('s:NeovimAsyncExitHandler')}
            if !s:IsWindows()
                let job_opts['detach'] = 1
            endif
            let job = jobstart(job_cmd, job_opts)
            if !empty(extra_heartbeats)
                call jobsend(job, extra_heartbeats . "\n")
            endif
        elseif s:IsWindows()
            if s:is_debug_on
                if !empty(extra_heartbeats)
                    let stdout = system('(' . s:JoinArgs(cmd) . ')', extra_heartbeats)
                else
                    let stdout = system('(' . s:JoinArgs(cmd) . ')')
                endif
            else
                if s:buffering_heartbeats_enabled
                    echo "[WakaTime] Error: Buffering heartbeats should be disabled on Windows without async support."
                endif
                exec 'silent !start /b cmd /c "' . s:JoinArgs(cmd) . ' > nul 2> nul"'
            endif
        else
            if s:is_debug_on
                if !empty(extra_heartbeats)
                    let stdout = system(s:JoinArgs(cmd), extra_heartbeats)
                else
                    let stdout = system(s:JoinArgs(cmd))
                endif
            else
                if !empty(extra_heartbeats)
                    let stdout = system(s:JoinArgs(cmd) . ' &', extra_heartbeats)
                else
                    let stdout = system(s:JoinArgs(cmd) . ' &')
                endif
            endif
        endif

        " restore shell
        let [&shell, &shellcmdflag, &shellredir] = [sh, shellcmdflag, shrd]

        let s:last_sent = localtime()

        " need to repaint in case a key was pressed while sending
        if !s:has_async && !s:nvim_async && s:redraw_setting != 'disabled'
            if s:redraw_setting == 'auto'
                if s:last_sent - start_time > 0
                    redraw!
                endif
            else
                redraw!
            endif
        endif

        if s:is_debug_on && !empty(stdout)
            echoerr '[WakaTime] Command: ' . s:JoinArgs(cmd) . "\n[WakaTime] Error: " . stdout
        endif
    endfunction

    function! s:GetHeartbeatsJson()
        let arr = []
        let loop_count = 1
        for heartbeat in s:heartbeats_buffer
            let heartbeat_str = '{"entity": "' . s:JsonEscape(heartbeat.entity) . '", '
            let heartbeat_str = heartbeat_str . '"timestamp": ' . s:OrderTime(heartbeat.time, loop_count) . ', '
            let heartbeat_str = heartbeat_str . '"is_write": '
            if heartbeat.is_write
                let heartbeat_str = heartbeat_str . 'true'
            else
                let heartbeat_str = heartbeat_str . 'false'
            endif
            if has_key(heartbeat, 'language')
                let heartbeat_str = heartbeat_str . ', "alternate_language": "' . s:JsonEscape(heartbeat.language) . '"'
            endif
            let heartbeat_str = heartbeat_str . '}'
            let arr = arr + [heartbeat_str]
            let loop_count = loop_count + 1
        endfor
        let s:heartbeats_buffer = []
        return '[' . join(arr, ',') . ']'
    endfunction

    function! s:OrderTime(time_str, loop_count)
        " Add a milisecond to a:time.
        " Time prevision doesn't matter, but order of heartbeats does.
        if !(a:time_str =~ "\.")
            let millisecond = s:n2s(a:loop_count)
            while strlen(millisecond) < 6
                let millisecond = '0' . millisecond
            endwhile
            return a:time_str . '.' . millisecond
        endif
        return a:time_str
    endfunction

    function! s:GetLastHeartbeat()
        if !s:last_heartbeat.last_activity_at || localtime() - s:last_heartbeat.last_activity_at > s:local_cache_expire
            if !filereadable(s:shared_state_file)
                return {'last_activity_at': 0, 'last_heartbeat_at': 0, 'file': ''}
            endif
            let last = readfile(s:shared_state_file, '', 3)
            if len(last) == 3
                let s:last_heartbeat.last_heartbeat_at = last[1]
                let s:last_heartbeat.file = last[2]
            endif
        endif
        return s:last_heartbeat
    endfunction

    function! s:SetLastHeartbeatInMemory(last_activity_at, last_heartbeat_at, file)
        let s:last_heartbeat = {'last_activity_at': a:last_activity_at, 'last_heartbeat_at': a:last_heartbeat_at, 'file': a:file}
    endfunction

    function! s:n2s(number)
        return substitute(printf('%d', a:number), ',', '.', '')
    endfunction

    function! s:SetLastHeartbeat(last_activity_at, last_heartbeat_at, file)
        call s:SetLastHeartbeatInMemory(a:last_activity_at, a:last_heartbeat_at, a:file)
        if !isdirectory(s:shared_state_parent_dir)
            call mkdir(s:shared_state_parent_dir, "p", "0o700")
        endif
        call writefile([s:n2s(a:last_activity_at), s:n2s(a:last_heartbeat_at), a:file], s:shared_state_file)
    endfunction

    function! s:EnoughTimePassed(now, last)
        let prev = a:last.last_heartbeat_at
        if a:now - prev > g:wakatime_HeartbeatFrequency * 60
            return s:true
        endif
        return s:false
    endfunction

    function! s:PromptForApiKey()
        let api_key = s:false
        let api_key = s:GetIniSetting('settings', 'api_key')
        if empty(api_key)
            let api_key = s:GetIniSetting('settings', 'apikey')
        endif

        let api_key = inputsecret("[WakaTime] Enter your wakatime.com api key: ", api_key)
        call s:SetIniSetting('settings', 'api_key', api_key)
    endfunction

    function! s:EnableDebugMode()
        call s:SetIniSetting('settings', 'debug', 'true')
        let s:is_debug_on = s:true
    endfunction

    function! s:DisableDebugMode()
        call s:SetIniSetting('settings', 'debug', 'false')
        let s:is_debug_on = s:false
    endfunction

    function! s:EnableScreenRedraw()
        call s:SetIniSetting('settings', 'vi_redraw', 'enabled')
        let s:redraw_setting = 'enabled'
    endfunction

    function! s:EnableScreenRedrawAuto()
        call s:SetIniSetting('settings', 'vi_redraw', 'auto')
        let s:redraw_setting = 'auto'
    endfunction

    function! s:DisableScreenRedraw()
        call s:SetIniSetting('settings', 'vi_redraw', 'disabled')
        let s:redraw_setting = 'disabled'
    endfunction

    function! s:InitAndHandleActivity(is_write)
        call s:SetupDebugMode()
        call s:SetupConfigFile()
        call s:SetupCLI()
        call s:HandleActivity(a:is_write)
    endfunction

    function! s:HandleActivity(is_write)
        let file = s:GetCurrentFile()
        if !empty(file) && file !~ "-MiniBufExplorer-" && file !~ "--NO NAME--" && file !~ "^term:"
            let last = s:GetLastHeartbeat()
            let now = localtime()

            " Create a heartbeat when saving a file, when the current file
            " changes, and when still editing the same file but enough time
            " has passed since the last heartbeat.
            if a:is_write || s:EnoughTimePassed(now, last) || file != last.file
                call s:AppendHeartbeat(file, now, a:is_write, last)
            else
                if now - s:last_heartbeat.last_activity_at > s:local_cache_expire
                    call s:SetLastHeartbeatInMemory(now, last.last_heartbeat_at, last.file)
                endif
            endif

            " When buffering heartbeats disabled, no need to re-check the
            " heartbeats buffer.
            if s:buffering_heartbeats_enabled

                " Only send buffered heartbeats every s:send_buffer_seconds
                if now - s:last_sent > s:send_buffer_seconds
                    call s:SendHeartbeats()
                endif
            endif
        endif
    endfunction

    function! g:WakaTimeToday(callback)
        let cmd = [s:wakatime_cli, '--today']

        let s:async_callback_today = a:callback
        if empty(a:callback)
            let s:async_callback_today = function('s:Print')
        endif

        if s:has_async
            if !s:IsWindows()
                let job_cmd = [&shell, &shellcmdflag, s:JoinArgs(cmd)]
            elseif &shell =~ 'sh\(\.exe\)\?$'
                let job_cmd = [&shell, '-c', s:JoinArgs(cmd)]
            else
                let job_cmd = [&shell, &shellcmdflag] + cmd
            endif
            let job = job_start(job_cmd, {
                \ 'stoponexit': '',
                \ 'callback': {channel, output -> s:AsyncTodayHandler(output, cmd)}})
        elseif s:nvim_async
            if s:IsWindows()
                let job_cmd = cmd
            else
                let job_cmd = [&shell, &shellcmdflag, s:JoinArgs(cmd)]
            endif
            let job_opts = {
                \ 'on_stdout': function('s:NeovimAsyncTodayOutputHandler'),
                \ 'on_stderr': function('s:NeovimAsyncTodayOutputHandler'),
                \ 'on_exit': function('s:NeovimAsyncTodayExitHandler')}
            if !s:IsWindows()
                let job_opts['detach'] = 1
            endif
            let s:nvim_async_output_today = ['']
            let job = jobstart(job_cmd, job_opts)
        else
            call s:async_callback_today(s:Chomp(system(s:JoinArgs(cmd))))
        endif
    endfunction

    function! g:WakaTimeFileExpert(callback)
        let file = s:GetCurrentFile()
        if empty(file)
            let file = s:GetLastHeartbeat().file
        endif
        let cmd = [s:wakatime_cli, '--file-experts', '--entity', file]

        let s:async_callback_file_expert = a:callback
        if empty(a:callback)
            let s:async_callback_file_expert = function('s:PrintFileExpert')
        endif

        if s:has_async
            if !s:IsWindows()
                let job_cmd = [&shell, &shellcmdflag, s:JoinArgs(cmd)]
            elseif &shell =~ 'sh\(\.exe\)\?$'
                let job_cmd = [&shell, '-c', s:JoinArgs(cmd)]
            else
                let job_cmd = [&shell, &shellcmdflag] + cmd
            endif
            let job = job_start(job_cmd, {
                \ 'stoponexit': '',
                \ 'callback': {channel, output -> s:AsyncFileExpertHandler(output, cmd)}})
        elseif s:nvim_async
            if s:IsWindows()
                let job_cmd = cmd
            else
                let job_cmd = [&shell, &shellcmdflag, s:JoinArgs(cmd)]
            endif
            let job_opts = {
                \ 'on_stdout': function('s:NeovimAsyncFileExpertOutputHandler'),
                \ 'on_stderr': function('s:NeovimAsyncFileExpertOutputHandler'),
                \ 'on_exit': function('s:NeovimAsyncFileExpertExitHandler')}
            if !s:IsWindows()
                let job_opts['detach'] = 1
            endif
            let s:nvim_async_output_file_expert = ['']
            let job = jobstart(job_cmd, job_opts)
        else
            call s:async_callback_file_expert(s:Chomp(system(s:JoinArgs(cmd))))
        endif
    endfunction

    function! g:WakaTimeCliLocation(callback)
        let s:cb = a:callback
        if empty(a:callback)
            let s:cb = function('s:Print')
        endif
        call s:cb(s:wakatime_cli)
    endfunction

    function! g:WakaTimeCliVersion(callback)
        let cmd = [s:wakatime_cli, '--version']

        let s:async_callback_version = a:callback
        if empty(a:callback)
            let s:async_callback_version = function('s:Print')
        endif

        if s:has_async
            if !s:IsWindows()
                let job_cmd = [&shell, &shellcmdflag, s:JoinArgs(cmd)]
            elseif &shell =~ 'sh\(\.exe\)\?$'
                let job_cmd = [&shell, '-c', s:JoinArgs(cmd)]
            else
                let job_cmd = [&shell, &shellcmdflag] + cmd
            endif
            let job = job_start(job_cmd, {
                \ 'stoponexit': '',
                \ 'callback': {channel, output -> s:AsyncVersionHandler(output, cmd)}})
        elseif s:nvim_async
            if s:IsWindows()
                let job_cmd = cmd
            else
                let job_cmd = [&shell, &shellcmdflag, s:JoinArgs(cmd)]
            endif
            let job_opts = {
                \ 'on_stdout': function('s:NeovimAsyncVersionOutputHandler'),
                \ 'on_stderr': function('s:NeovimAsyncVersionOutputHandler'),
                \ 'on_exit': function('s:NeovimAsyncVersionExitHandler')}
            if !s:IsWindows()
                let job_opts['detach'] = 1
            endif
            let s:nvim_async_output_version = ['']
            let job = jobstart(job_cmd, job_opts)
        else
            call s:async_callback_version(s:Chomp(system(s:JoinArgs(cmd))))
        endif
    endfunction

    function! s:Print(msg)
        echo a:msg
    endfunction

    function! s:PrintToday(msg)
        echo "Today: " . a:msg
    endfunction

    function! s:PrintFileExpert(msg)
        let output = a:msg
        if empty(output)
            let output = 'No data on this file.'
        endif
        echo output
    endfunction

    function! s:Executable(path)
        if !empty(a:path) && executable(a:path)
            return s:true
        endif
        return s:false
    endfunction

    function! s:Contains(string, substr)
        if empty(a:string) || empty(a:substr)
            return s:false
        endif
        if stridx(a:string, a:substr) > -1
            return s:true
        endif
        return s:false
    endfunction

" }}}


" Async Handlers {{{

    function! s:AsyncHandler(output, cmd)
        if s:is_debug_on && !empty(s:StripWhitespace(a:output))
            echoerr '[WakaTime] Command: ' . s:JoinArgs(a:cmd) . "\n[WakaTime] Error: " . a:output
        endif
    endfunction

    function! s:NeovimAsyncOutputHandler(job_id, output, event)
        let s:nvim_async_output[-1] .= a:output[0]
        call extend(s:nvim_async_output, a:output[1:])
    endfunction

    function! s:NeovimAsyncExitHandler(job_id, exit_code, event)
        let output = s:StripWhitespace(join(s:nvim_async_output, "\n"))
        if a:exit_code == s:exit_code_api_key_error
            let output .= 'Invalid API Key'
        endif
        if (s:is_debug_on || a:exit_code == s:exit_code_config_parse_error || a:exit_code == s:exit_code_api_key_error) && !empty(output)
            echoerr printf('[WakaTime] Error %d: %s', a:exit_code, output)
        endif
    endfunction

    function! s:AsyncTodayHandler(output, cmd)
        call s:async_callback_today(a:output)
    endfunction

    function! s:NeovimAsyncTodayOutputHandler(job_id, output, event)
        let s:nvim_async_output_today[-1] .= a:output[0]
        call extend(s:nvim_async_output_today, a:output[1:])
    endfunction

    function! s:NeovimAsyncTodayExitHandler(job_id, exit_code, event)
        let output = s:StripWhitespace(join(s:nvim_async_output_today, "\n"))
        if a:exit_code == s:exit_code_api_key_error
            let output .= 'Invalid API Key'
        endif
        call s:async_callback_today(output)
    endfunction

    function! s:AsyncFileExpertHandler(output, cmd)
        call s:async_callback_file_expert(a:output)
    endfunction

    function! s:NeovimAsyncFileExpertOutputHandler(job_id, output, event)
        let s:nvim_async_output_file_expert[-1] .= a:output[0]
        call extend(s:nvim_async_output_file_expert, a:output[1:])
    endfunction

    function! s:NeovimAsyncFileExpertExitHandler(job_id, exit_code, event)
        let output = s:StripWhitespace(join(s:nvim_async_output_file_expert, "\n"))
        if a:exit_code == s:exit_code_api_key_error
            let output .= 'Invalid API Key'
        endif
        call s:async_callback_file_expert(output)
    endfunction

    function! s:AsyncVersionHandler(output, cmd)
        call s:async_callback_version(a:output)
    endfunction

    function! s:NeovimAsyncVersionOutputHandler(job_id, output, event)
        let s:nvim_async_output_version[-1] .= a:output[0]
        call extend(s:nvim_async_output_version, a:output[1:])
    endfunction

    function! s:NeovimAsyncVersionExitHandler(job_id, exit_code, event)
        let output = s:StripWhitespace(join(s:nvim_async_output_version, "\n"))
        if a:exit_code == s:exit_code_api_key_error
            let output .= 'Invalid API Key'
        endif
        call s:async_callback_version(output)
    endfunction

    function! s:AsyncInstallHandler(output)
        if s:is_debug_on && !empty(s:StripWhitespace(a:output))
            echo '[WakaTime] ' . a:output
            call s:InstallCLI(s:false)
        endif
    endfunction

    function! s:NeovimAsyncInstallOutputHandler(job_id, output, event)
        let s:nvim_async_output[-1] .= a:output[0]
        call extend(s:nvim_async_output, a:output[1:])
    endfunction

    function! s:NeovimAsyncInstallExitHandler(job_id, exit_code, event)
        let output = s:StripWhitespace(join(s:nvim_async_output, "\n"))
        if s:is_debug_on && (a:exit_code != 0 || !empty(output))
            echo printf('[WakaTime] %d: %s', a:exit_code, output)
            call s:InstallCLI(s:false)
        endif
    endfunction

" }}}


call s:Init()


" Autocommand Events {{{

    augroup Wakatime
        autocmd BufEnter,VimEnter * call s:InitAndHandleActivity(s:false)
        autocmd CursorHold,CursorHoldI * call s:HandleActivity(s:false)
        autocmd BufWritePost * call s:HandleActivity(s:true)
        if exists('##QuitPre')
            autocmd QuitPre * call s:SendHeartbeats()
        endif
    augroup END

" }}}


" Plugin Commands {{{

    :command -nargs=0 WakaTimeApiKey call s:PromptForApiKey()
    :command -nargs=0 WakaTimeDebugEnable call s:EnableDebugMode()
    :command -nargs=0 WakaTimeDebugDisable call s:DisableDebugMode()
    :command -nargs=0 WakaTimeScreenRedrawDisable call s:DisableScreenRedraw()
    :command -nargs=0 WakaTimeScreenRedrawEnable call s:EnableScreenRedraw()
    :command -nargs=0 WakaTimeScreenRedrawEnableAuto call s:EnableScreenRedrawAuto()
    :command -nargs=0 WakaTimeToday call g:WakaTimeToday(function('s:Print'))
    :command -nargs=0 WakaTimeFileExpert call g:WakaTimeFileExpert(function('s:PrintFileExpert'))
    :command -nargs=0 WakaTimeCliLocation call g:WakaTimeCliLocation(function('s:Print'))
    :command -nargs=0 WakaTimeCliVersion call g:WakaTimeCliVersion(function('s:Print'))

" }}}


" Restore wildignore option
if s:wildignore != ""
    let &wildignore=s:wildignore
endif

" Restore cpoptions
let &cpo = s:old_cpo
