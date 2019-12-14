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

function coveragepy#Show()
    let l:params = s:GetCoverageParams()
    if !empty(l:params)
        :call CoveragePyShow(l:params.cov_file, l:params.filename)
    endif
endfunction

function coveragepy#Toggle()
    let l:params = s:GetCoverageParams()
    if !empty(l:params)
        :call CoveragePyToggle(l:params.cov_file, l:params.filename)
    endif
endfunction

function coveragepy#NextProblem()
    let l:params = s:GetCoverageParams()
    if !empty(l:params)
        :call CoveragePyNext(l:params.cov_file, l:params.filename, line("."))
    endif
endfunction

function coveragepy#PytestContext()
    let l:params = s:GetCoverageParams()
    if !empty(l:params)
        :call CoveragePyTestContext(l:params.cov_file, l:params.filename, line("."))
    endif
endfunction
