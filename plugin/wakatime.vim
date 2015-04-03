" ============================================================================
" File:        wakatime.vim
" Description: Automatic time tracking for Vim.
" Maintainer:  WakaTime <support@wakatime.com>
" License:     BSD, see LICENSE.txt for more details.
" Website:     https://wakatime.com/
" ============================================================================

let s:VERSION = '3.0.9'


" Init {{{

    " Check Vim version
    if v:version < 700
        echoerr "This plugin requires vim >= 7."
        finish
    endif

    " Only load plugin once
    if exists("g:loaded_wakatime")
        finish
    endif
    let g:loaded_wakatime = 1

    " Backup & Override cpoptions
    let s:old_cpo = &cpo
    set cpo&vim

    " To be backwards compatible, rename config file
    if filereadable(expand("$HOME/.wakatime"))
        exec "silent !mv" expand("$HOME/.wakatime") expand("$HOME/.wakatime.conf")
    endif
    if filereadable(expand("$HOME/.wakatime.conf"))
        if !filereadable(expand("$HOME/.wakatime.cfg"))
            let contents = ['[settings]'] + readfile(expand("$HOME/.wakatime.conf"), '')
            call writefile(contents, expand("$HOME/.wakatime.cfg"))
            call delete(expand("$HOME/.wakatime.conf"))
        endif
    endif

    " Set default python binary location
    if !exists("g:wakatime_PythonBinary")
        let g:wakatime_PythonBinary = 'python'
    endif

    " Set default heartbeat frequency in minutes
    if !exists("g:wakatime_HeartbeatFrequency")
        let g:wakatime_HeartbeatFrequency = 2
    endif

    " Globals
    let s:plugin_directory = expand("<sfile>:p:h") . '/'
    let s:config_file_exists = 0

" }}}


" Function Definitions {{{

    function! s:SetupConfigFile()
        if !s:config_file_exists
            " Create config file if does not exist
            if !filereadable(expand("$HOME/.wakatime.cfg"))
                let key = input("[WakaTime] Enter your wakatime.com api key: ")
                if key != ''
                    call writefile(['[settings]', 'debug = false', printf("api_key = %s", key), 'hidefilenames = false', 'ignore =', '    ^COMMIT_EDITMSG$', '    ^TAG_EDITMSG$'], expand("$HOME/.wakatime.cfg"))
                    echo "[WakaTime] Setup complete! Visit http://wakatime.com to view your logged time."
                endif
            endif
            let s:config_file_exists = 1
        endif
    endfunction

    function! s:GetCurrentFile()
        return expand("%:p")
    endfunction

    function! s:Api(targetFile, time, is_write, last)
        let targetFile = a:targetFile
        if targetFile == ''
            let targetFile = a:last[2]
        endif
        if targetFile != ''
            let python_bin = g:wakatime_PythonBinary
            if has('win32') || has('win64')
                if python_bin == 'python'
                    let python_bin = 'pythonw'
                endif
            endif
            let cmd = [python_bin, '-W', 'ignore', s:plugin_directory . 'packages/wakatime/cli.py']
            let cmd = cmd + ['--file', shellescape(targetFile)]
            let cmd = cmd + ['--plugin', shellescape(printf('vim/%d vim-wakatime/%s', v:version, s:VERSION))]
            if a:is_write
                let cmd = cmd + ['--write']
            endif
            "let cmd = cmd + ['--verbose']
            if has('win32') || has('win64')
                exec 'silent !start /min cmd /c "' . join(cmd, ' ') . '"'
            else
                exec 'silent !' . join(cmd, ' ') . ' &'
            endif
            call s:SetLastAction(a:time, a:time, targetFile)
        endif
    endfunction
    
    function! s:GetLastAction()
        if !filereadable(expand("$HOME/.wakatime.data"))
            return [0, 0, '']
        endif
        let last = readfile(expand("$HOME/.wakatime.data"), '', 3)
        if len(last) != 3
            return [0, 0, '']
        endif
        return last
    endfunction
    
    function! s:SetLastAction(time, last_update, targetFile)
        call writefile([substitute(printf('%d', a:time), ',', '.', ''), substitute(printf('%d', a:last_update), ',', '.', ''), a:targetFile], expand("$HOME/.wakatime.data"))
    endfunction

    function! s:GetChar()
        let c = getchar()
        if c =~ '^\d\+$'
          let c = nr2char(c)
        endif
        return c
    endfunction

    function! s:EnoughTimePassed(now, last)
        let prev = a:last[0]
        if a:now - prev > g:wakatime_HeartbeatFrequency * 60
            return 1
        endif
        return 0
    endfunction
    
" }}}


" Event Handlers {{{

    function! s:normalAction()
        call s:SetupConfigFile()
        let targetFile = s:GetCurrentFile()
        let now = localtime()
        let last = s:GetLastAction()
        if s:EnoughTimePassed(now, last) || targetFile != last[2]
            call s:Api(targetFile, now, 0, last)
        endif
    endfunction

    function! s:writeAction()
        let targetFile = s:GetCurrentFile()
        let now = localtime()
        let last = s:GetLastAction()
        call s:Api(targetFile, now, 1, last)
    endfunction

" }}}


" Autocommand Events {{{

    augroup Wakatime
        autocmd!
        autocmd BufEnter * call s:normalAction()
        autocmd VimEnter * call s:normalAction()
        autocmd BufWritePost * call s:writeAction()
        autocmd CursorMoved,CursorMovedI * call s:normalAction()
    augroup END

" }}}


" Restore cpoptions
let &cpo = s:old_cpo
