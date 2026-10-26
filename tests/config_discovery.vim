" Used by config_discovery.py in an isolated editor process for each case.
set nomore
let &wildignore = '*.o'
let s:original_wildignore = &wildignore
let s:original_cpo = &cpo
let s:root = fnamemodify(expand('<sfile>:p'), ':h:h')
let &runtimepath = s:root . ',' . &runtimepath

function! s:WaitForCliCalls(count)
    for attempt in range(1000)
        if filereadable($WAKATIME_TEST_CALL_LOG) && len(readfile($WAKATIME_TEST_CALL_LOG)) >= a:count
            return
        endif
        sleep 10m
    endfor
    throw 'Timed out waiting for CLI calls'
endfunction

try
    if has('nvim')
        lua require('wakatime').setup({ cli_path = vim.env.WAKATIME_TEST_CLI })
    elseif !empty($WAKATIME_TEST_CLI)
        let g:wakatime_CLIPath = $WAKATIME_TEST_CLI
    endif
    execute 'source ' . fnameescape(s:root . '/plugin/wakatime.vim')

    if &wildignore !=# s:original_wildignore || &cpo !=# s:original_cpo
        throw 'Plugin did not restore wildignore and cpoptions after loading'
    endif

    if has('nvim')
        lua << EOF
local setup = require('wakatime').setup
for i = 1, math.huge do
  local name, state = debug.getupvalue(setup, i)
  if not name then error('WakaTime state not found') end
  if name == 'state' then
    vim.g.wakatime_test_state = {
      config_file = state.config_file,
      home = state.home,
      shared_state_file = state.shared_state_file,
      cli = state.wakatime_cli,
      redraw_setting = state.config.redraw_setting,
    }
    break
  end
end
EOF
    else
        for s:script in getscriptinfo()
            if s:script.name ==# s:root . '/plugin/wakatime.vim'
                let s:state = getscriptinfo({'sid': s:script.sid})[0].variables
                let g:wakatime_test_state = {
                            \ 'config_file': s:state.config_file,
                            \ 'home': s:state.home,
                            \ 'shared_state_file': s:state.shared_state_file,
                            \ 'cli': s:state.wakatime_cli,
                            \ 'redraw_setting': s:state.redraw_setting,
                            \ }
                break
            endif
        endfor
    endif

    call writefile([json_encode(g:wakatime_test_state)], $WAKATIME_TEST_OUTPUT)
    " Stop before writing if discovery chose an unexpected path.
    if fnamemodify(g:wakatime_test_state.config_file, ':p') !=# fnamemodify($WAKATIME_TEST_CONFIG, ':p')
        quitall!
    endif
    if $WAKATIME_TEST_RUN_CLI ==# '1'
        if has('nvim')
            " Command failures are checked in the fixture log for every call.
            lua vim.notify = function() end
        endif
        call feedkeys("\<C-U>" . $WAKATIME_TEST_API_KEY . "\<CR>", 't')
        WakaTimeApiKey
        WakaTimeStatusBarDisable
        " Let Neovim's deferred initial check run while the buffer is unnamed.
        sleep 150m
        execute 'noautocmd edit ' . fnameescape($WAKATIME_TEST_SAMPLE)
        WakaTimeToday
        call s:WaitForCliCalls(1)
        WakaTimeFileExpert
        call s:WaitForCliCalls(2)
        WakaTimeCliVersion
        call s:WaitForCliCalls(3)
        doautocmd BufWritePost
        doautocmd QuitPre
        call s:WaitForCliCalls(4)
        if has('nvim')
            WakaTimeStatusBarEnable
            lua require('wakatime').statusline()
            call s:WaitForCliCalls(5)
        endif
    endif
    if !empty($WAKATIME_TEST_REMOVE_DIR)
        call delete($WAKATIME_TEST_REMOVE_DIR, 'rf')
    endif
    if $WAKATIME_TEST_SETUP ==# '1'
        doautocmd VimEnter
    endif
    if $WAKATIME_TEST_WRITE ==# '1'
        WakaTimeScreenRedrawEnable
    endif
catch
    call writefile([v:exception . ' at ' . v:throwpoint], $WAKATIME_TEST_ERROR)
    cquit
endtry
quitall!
