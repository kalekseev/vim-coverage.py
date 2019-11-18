if !exists("g:coveragepy_virtualenv")
  if has("nvim")
    let g:coveragepy_virtualenv = "~/.local/share/nvim/coveragepy"
  else
    let g:coveragepy_virtualenv = "~/.vim/coveragepy"
  endif
endif

let g:coveragepy_sign_offset = get(g:, 'coveragepy_sign_offset', 5000000)

let s:plugin_path = expand('<sfile>:p:h')
let s:supports_sign_groups = has('nvim-0.4.2') || (v:version >= 801 && has('patch614'))

python3 << endpython3
import os
import sys
import vim
plugin_path = vim.eval("s:plugin_path")
python_module_path = os.path.abspath('%s/../python' % (plugin_path))
sys.path.insert(0, python_module_path)
import vim_coverage_env
vim_coverage_env.init()
import vim_coverage
vim.eval("s:supports_sign_groups") and vim_coverage.downgrade_editor()
vim_coverage.editor.sign_offset = vim.eval("g:coveragepy_sign_offset")
del sys.path[:1]
endpython3

function! s:FindCoverageFile() abort
    let l:cov_file = findfile('.coverage', '.;')
    if empty(l:cov_file)
        :echohl WarningMsg | echo "Can't find .coverage file." | echohl None
        return
    endif
    return fnamemodify(l:cov_file, ':p')
endfunction

function! s:GetCoverageParams() abort
    let l:cov_file = s:FindCoverageFile()
    if empty(l:cov_file)
        return
    endif
    let l:filename = fnamemodify(bufname("%"), ':p')
    if empty(l:filename) || expand('%:e') != 'py'
        :echohl WarningMsg | echo "Not a python file." | echohl None
        return
    endif
    return {"cov_file": l:cov_file, "filename": l:filename}
endfunction

function coveragepy#Coverage()
    let l:params = s:GetCoverageParams()
    if !empty(l:params)
        :py3 vim_coverage.coverage_show(**vim.eval("l:params"))
    endif
endfunction

function coveragepy#CoverageToggle()
    let l:params = s:GetCoverageParams()
    if !empty(l:params)
        :py3 vim_coverage.coverage_toggle(**vim.eval("l:params"))
    endif
endfunction

function coveragepy#CoverageLine()
    let l:params = s:GetCoverageParams()
    if !empty(l:params)
        let l:params.line = line(".")
        :py3 vim_coverage.coverage_line(**vim.eval("l:params"))
    endif
endfunction

function coveragepy#CoverageNext()
    let l:params = s:GetCoverageParams()
    if !empty(l:params)
        let l:params.line = line(".")
        :py3 vim_coverage.coverage_next_problem(**vim.eval("l:params"))
    endif
endfunction

function coveragepy#CoverageUpgrade()
    :py3 vim_coverage_env.init(upgrade=True)
endfunction

function coveragepy#CoverageVersion()
    :py3 vim_coverage.coverage_version()
endfunction
