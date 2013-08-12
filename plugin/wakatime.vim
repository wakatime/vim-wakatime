" ============================================================================
" File:        wakatime.vim
" Description: Automatic time tracking for Vim.
" Maintainer:  Wakati.Me <support@wakatime.com>
" ============================================================================

let s:VERSION = '1.0.0'


" Init {{{

    " Check Vim version
    if v:version < 700
        echoerr "This plugin requires vim >= 7."
        finish
    endif

    " Check for Python support
    if !has('python')
        echoerr "This plugin requires Vim to be compiled with Python support."
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
    
    " Create config file if does not exist
    if !filereadable(expand("$HOME/.wakatime.conf"))
        let key = input("Enter your WakaTi.me api key: ")
        if key != ''
            call writefile([printf("api_key=%s", key)], expand("$HOME/.wakatime.conf"))
            echo "WakaTi.me setup complete! Visit https://wakati.me to view your logged time."
        endif
    endif

    " Set default action frequency in minutes
    if !exists("g:wakatime_ActionFrequency")
        let g:wakatime_ActionFrequency = 5
    endif

    " Globals
    let s:plugin_directory = expand("<sfile>:p:h") . '/'
    let s:last_action = 0
    let s:fresh = 1

    " Import things python needs
    python import time
    python import vim

" }}}


" Function Definitions {{{

    function! s:GetCurrentFile()
        return expand("%:p")
    endfunction

    function! s:GetCurrentTime()
        python vim.command('let current_time=%f' % time.time())
        return current_time
    endfunction

    function! s:Api(targetFile, time, is_write, last)
        let targetFile = a:targetFile
        if targetFile == ''
            let targetFile = a:last[2]
        endif
        if targetFile != ''
            let cmd = ['python', s:plugin_directory . 'packages/wakatime/wakatime-cli.py']
            let cmd = cmd + ['--file', shellescape(targetFile)]
            let cmd = cmd + ['--time', printf('%f', a:time)]
            let cmd = cmd + ['--plugin', printf('vim-wakatime/%s', s:VERSION)]
            if a:is_write
                let cmd = cmd + ['--write']
            endif
            "let cmd = cmd + ['--verbose']
            exec 'silent !' . join(cmd, ' ') . ' &'
            call s:SetLastAction(a:time, a:time, targetFile)
        endif
    endfunction
    
    function! s:GetLastAction()
        if !filereadable(expand("$HOME/.wakatime.data"))
            return [0.0, '', 0.0]
        endif
        let last = readfile(expand("$HOME/.wakatime.data"), '', 3)
        if len(last) != 3
            return [0.0, '', 0.0]
        endif
        return [str2float(last[0]), str2float(last[1]), last[2]]
    endfunction
    
    function! s:SetLastAction(time, last_update, targetFile)
        let s:fresh = 0
        call writefile([printf('%f', a:time), printf('%f', a:last_update), a:targetFile], expand("$HOME/.wakatime.data"))
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
        if a:now - prev > g:wakatime_ActionFrequency * 60
            return 1
        endif
        return 0
    endfunction
    
" }}}


" Event Handlers {{{

    function! s:normalAction()
        let targetFile = s:GetCurrentFile()
        let now = s:GetCurrentTime()
        let last = s:GetLastAction()
        if s:EnoughTimePassed(now, last) || targetFile != last[2]
            call s:Api(targetFile, now, 0, last)
        else
            if now - last[1] > 5
                call s:SetLastAction(last[0], now, targetFile)
            endif
        endif
    endfunction

    function! s:writeAction()
        let targetFile = s:GetCurrentFile()
        let now = s:GetCurrentTime()
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
