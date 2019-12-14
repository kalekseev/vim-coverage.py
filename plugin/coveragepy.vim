" vim-coverage.py
" Author: Konstantin Alekseev
" Version: 0.2


if v:version < 700 || !has('python3')
    echo "This script requires vim7.0+ with Python 3.6 support."
    finish
endif

if exists("g:load_vim_coveragepy")
   finish
endif

let g:load_vim_coveragepy = 1

highlight default CoveragePyOk ctermfg=114 guifg=#98C379
highlight default link CoveragePyWarn WarningMsg
highlight default link CoveragePyError ErrorMsg

sign define coverageOk text=▴▴ texthl=CoveragePyOk
sign define coverageWarn text=◊◊ texthl=CoveragePyWarn
sign define coverageErr text=▵▵ texthl=CoveragePyError

command! CoveragePy :call coveragepy#Show()
command! CoveragePyToggle :call coveragepy#Toggle()
command! CoveragePytestContext :call coveragepy#PytestContext()
command! CoveragePyNext :call coveragepy#NextProblem()

if has('nvim')
    finish
endif

let s:py = yarp#py3('vim_coveragepy_wrap')

func! CoveragePyShow(c, f)
    return s:py.call('show', a:c, a:f)
endfunc

func! CoveragePyToggle(c, f)
    return s:py.call('toggle', a:c, a:f)
endfunc

func! CoveragePyNext(c, f, l)
    return s:py.call('go_next_problem', a:c, a:f, a:l)
endfunc

func! CoveragePyTestContext(c, f, l)
    return s:py.call('show_pytest_context', a:c, a:f, a:l)
endfunc
