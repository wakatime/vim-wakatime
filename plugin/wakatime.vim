" ============================================================================
" File:        wakatime.vim
" Description: invisible time tracker using Wakati.Me
" Maintainer:  Wakati.Me <support@wakatime.com>
" Version: 0.1.2
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

" Check for required user-defined settings
if !exists("g:wakatime_api_key")
    if filereadable(expand("$HOME/.wakatime"))
        for s:line in readfile(expand("$HOME/.wakatime"))
            let s:setting = split(s:line, "=")
            if s:setting[0] == "api_key"
                let g:wakatime_api_key = s:setting[1]
            endif
        endfor
    endif
    if !exists("g:wakatime_api_key")
        finish
    endif
endif

" Only load plugin once
if exists("g:loaded_wakatime")
    finish
endif
let g:loaded_wakatime = 1

" Backup & Override cpoptions
let s:old_cpo = &cpo
set cpo&vim

let s:plugin_directory = expand("<sfile>:p:h")

" Set default updatetime
if !exists("g:wakatime_updatetime")
    let g:wakatime_updatetime = 15 " 15 minutes
endif

" We are not away until getting a CursorHold event
let s:away_start = 0

python << ENDPYTHON
import vim
import uuid
import time

instance_id = str(uuid.uuid4())
vim.command('let s:instance_id = "%s"' % instance_id)
ENDPYTHON

" }}}


" Function Definitions {{{

function! s:initVariable(var, value)
    if !exists(a:var)
        exec 'let ' . a:var . ' = ' . "'" . substitute(a:value, "'", "''", "g") . "'"
        return 1
    endif
    return 0
endfunction

function! s:setUpdateTime()
    if &updatetime < 60 * 1000 * 2
        let &updatetime = g:wakatime_updatetime * 60 * 1000
    endif
endfunction

function! s:GetCurrentFile()
    return expand("%:p")
endfunction

function! s:api(type, task)
    if a:task != ''
        exec "silent !python " . s:plugin_directory . "/wakatime.py --key" g:wakatime_api_key "--instance" s:instance_id "--action" a:type "--task" shellescape(a:task) . " &"
    endif
endfunction

function! s:api_with_time(type, task, time)
    if a:task != ''
        exec "silent !python " . s:plugin_directory . "/wakatime.py --key" g:wakatime_api_key "--instance" s:instance_id "--action" a:type "--task" shellescape(a:task) "--time" printf("%f", a:time) . " &"
    endif
endfunction

function! s:getchar()
    let c = getchar()
    if c =~ '^\d\+$'
      let c = nr2char(c)
    endif
    return c
endfunction

function! Wakatime_isAway()
    return s:away_start
endfunction

function! s:allServersAway()
    if has('clientserver')
        let servers = split(serverlist())
        for server in servers
            if server != v:servername
                if !remote_expr(server,'Wakatime_isAway()')
                    return 0
                endif
            endif
        endfor
    endif
    return 1
endfunction

" }}}


" Event Handlers {{{

function! s:bufenter()
    let task = s:GetCurrentFile()
    call s:api("open_file", task)
endfunction

function! s:bufleave()
    let task = s:GetCurrentFile()
    call s:api("close_file", task)
endfunction

function! s:vimenter()
    let task = s:GetCurrentFile()
    call s:api("open_editor", task)
endfunction

function! s:vimleave()
    let task = s:GetCurrentFile()
    call s:api("quit_editor", task)
endfunction

function! s:bufwrite()
    let task = s:GetCurrentFile()
    call s:api("write_file", task)
endfunction

function! s:cursorhold()
    let s:away_task = s:GetCurrentFile()
    python vim.command("let s:away_start=%f" % (time.time() - (float(vim.eval("&updatetime")) / 1000.0)))
    autocmd Wakatime CursorMoved,CursorMovedI * call s:cursormoved()
endfunction

function! s:cursormoved()
    autocmd! Wakatime CursorMoved,CursorMovedI *

    " Don't do anything unless all other Vim instances are also away
    if !s:allServersAway()
        let s:away_start = 0
        call s:api("ping", s:away_task)
        return
    endif

    python vim.command("let away_end=%f" % time.time())
    let away_unit = "minutes"
    let away_duration = (away_end - s:away_start) / 60
    if away_duration < 2
        call s:setUpdateTime()
        return
    endif
    if away_duration > 59
        let away_duration = away_duration / 60
        let away_unit = "hours"
    endif
    if away_duration > 59
        let away_duration = away_duration / 60
        let away_unit = "days"
    endif
    let answer = input(printf("You were away %.f %s. Add time to current file? (y/n)", away_duration, away_unit))
    if answer != "y"
        call s:api_with_time("minimize_editor", s:away_task, s:away_start)
        call s:api_with_time("maximize_editor", s:away_task, away_end)
    else
        call s:api("ping", s:away_task)
    endif
    let s:away_start = 0
    "redraw!
endfunction

" }}}


call s:setUpdateTime()


" Autocommand Events {{{

augroup Wakatime
    autocmd!
    autocmd BufEnter * call s:bufenter()
    autocmd BufLeave * call s:bufleave()
    autocmd VimEnter * call s:vimenter()
    autocmd VimLeave * call s:vimleave()
    autocmd BufWritePost * call s:bufwrite()
    autocmd CursorHold,CursorHoldI * call s:cursorhold()
augroup END

" }}}


" Restore cpoptions
let &cpo = s:old_cpo
