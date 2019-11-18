" vim-coverage.py
" Author: Konstantin Alekseev
" Version: 0.1


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

command! CoveragePy :call coveragepy#Coverage()
command! CoveragePyToggle :call coveragepy#CoverageToggle()
command! CoveragePyLine :call coveragepy#CoverageLine()
command! CoveragePyNext :call coveragepy#CoverageNext()
command! CoveragePyUpgrade :call coveragepy#CoverageUpgrade()
command! CoveragePyVersion :call coveragepy#CoverageVersion()
