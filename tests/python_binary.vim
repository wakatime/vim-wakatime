" Run from the repository root:
" vim -Nu NONE -i NONE -n -es -S tests/python_binary.vim

let s:plugin = fnamemodify(expand('<sfile>:p'), ':h:h') . '/plugin/wakatime.vim'
let s:vim_binary = exepath(v:progpath)
let s:test_home = tempname()
call mkdir(s:test_home, 'p')
let $WAKATIME_HOME = s:test_home
let g:wakatime_CLIPath = s:vim_binary

try
    execute 'source ' . fnameescape(s:plugin)
    for s:script in getscriptinfo()
        if s:script.name ==# s:plugin
            let s:GetPythonBinary = function('<SNR>' . s:script.sid . '_GetPythonBinary')
            break
        endif
    endfor

    unlet! g:wakatime_PythonBinary
    let s:fallback = s:GetPythonBinary()

    " The selector only checks whether the configured file is executable.
    " Reuse Vim itself as a fixture without needing another Python install.
    let g:wakatime_PythonBinary = s:vim_binary
    call assert_equal(s:vim_binary, s:GetPythonBinary(), 'Use the configured executable')

    let g:wakatime_PythonBinary = s:test_home . '/missing-python'
    call assert_equal(s:fallback, s:GetPythonBinary(), 'Fall back for a missing executable')

    unlet g:wakatime_PythonBinary
    call assert_equal(s:fallback, s:GetPythonBinary(), 'Fall back when the option is unset')
finally
    call delete(s:test_home, 'rf')
endtry

if !empty(v:errors)
    for s:error in v:errors
        echomsg s:error
    endfor
    cquit
endif
quitall!
