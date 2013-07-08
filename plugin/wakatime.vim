" ============================================================================
" File:        wakatime.vim
" Description: Automatic time tracking for Vim.
" Maintainer:  Wakati.Me <support@wakatime.com>
" Version:     0.2.1
" ============================================================================


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

    " Set default away minutes
    if !exists("g:wakatime_AwayMinutes")
        let g:wakatime_AwayMinutes = 10
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
        python vim.command('let current_time="%f"' % time.time())
        return current_time
    endfunction

    function! s:Api(targetFile, time, endtime, is_write, last)
        let targetFile = a:targetFile
        if targetFile == ''
            let targetFile = a:last[1]
        endif
        if targetFile != ''
            let extras = ''
            if a:is_write
                let extras = extras . '--write'
            endif
            if a:endtime
                let extras = extras . '--endtime ' . printf('%f', a:endtime)
            endif
            exec "silent !python" s:plugin_directory . "packages/wakatime/wakatime.py --file" shellescape(targetFile) "--time" printf('%s', a:time) extras . " &"
            let time = a:time
            if a:endtime && time < a:endtime
                let time = a:endtime
            endif
            call s:SetLastAction(time, targetFile)
        endif
    endfunction
    
    function! s:GetLastAction()
        if !filereadable(expand("$HOME/.wakatime.data"))
            return [0, '']
        endif
        let last = readfile(expand("$HOME/.wakatime.data"), '', 2)
        if len(last) != 2
            return [0, '']
        endif
        return [str2float(last[0]), last[1]]
    endfunction
    
    function! s:SetLastAction(time, targetFile)
        let s:fresh = 0
        call writefile([a:time, a:targetFile], expand("$HOME/.wakatime.data"))
    endfunction

    function! s:GetChar()
        let c = getchar()
        if c =~ '^\d\+$'
          let c = nr2char(c)
        endif
        return c
    endfunction
    
    function! s:EnoughTimePassed(now, prev)
        if a:now - a:prev >= 299
            return 1
        endif
        return 0
    endfunction
    
    function! s:Away(now, last)
        if s:fresh || a:last[0] < 1
            return 0
        endif

        let duration = a:now - a:last[0]
        if duration > g:wakatime_AwayMinutes * 60
            let units = 'seconds'
            if duration > 59
                let duration = round(duration / 60)
                let units = 'minutes'
            endif
            if duration > 59
                let duration = round(duration / 60)
                let units = 'hours'
            endif
            if duration > 24
                let duration = round(duration / 24)
                let units = 'days'
            endif
            let answer = input(printf("You were away %.f %s. Add time to current file? (y/n)", duration, units))
            if answer != "y"
                return 1
            endif
            return 0
        endif
    endfunction

" }}}


" Event Handlers {{{

    function! s:normalAction()
        let targetFile = s:GetCurrentFile()
        let now = s:GetCurrentTime()
        let last = s:GetLastAction()
        if s:EnoughTimePassed(now, last[0]) || targetFile != last[1]
            if s:Away(now, last)
                call s:Api(targetFile, last[0], now, 0, last)
            else
                call s:Api(targetFile, now, 0, 0, last)
            endif
        endif
    endfunction

    function! s:writeAction()
        call s:Api(s:GetCurrentFile(), s:GetCurrentTime(), 0, 1, s:GetLastAction())
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
