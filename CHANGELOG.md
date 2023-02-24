## 1.2.0 (2023-02-24)

### Feat

- call different tox environment due to how OS call python binary
- unify workflow, deactivating others
- removed complete workflow, cibuildwheel does not build pure python package
- add python-active-versions and check-python-versions


### Fix

- coverage file name
- remove invalid signal CTRL_BREAK for windows
- remove invalid signal value on windows
- fallback to previous workflows, adding OS
- remove unnecessary else after raise or return

## 1.1.0 (2023-02-20)

### Feat

- new test for json generation, remove temp files
- new test for dict saving
- handle signals, saving partial dict.
- use event instead of bool to prompt waiting user
- save partial dict when nothing listened, skip combination if previously saved
- extract partial_inc from file saved, input filename as path in init
- remove tmp file when saving final dict
- load partial file plus tests
- save partial dictionary listened
- wait user input after a set of code listened, save to json that will be loaded on nex run to skip already read combinations

### Fix

- wait before first code if codes were loaded from previous file

## 1.0.0 (2022-12-18)

### Feat

- tests on skip field execution
- test no code learnt case
- increate test complexity
- new tests with all json combinations
- license managed with tox env
- empty default tuple
- new tests
- refact skipped combination, added print
- util tests

### Fix

- create section for final json

## 0.2.0 (2022-12-09)

### Feat

- github pages on release
- build docs with tox

## 0.1.3 (2022-12-09)

### Fix

- sphinx file generation
- using github action for conventional commits

## 0.1.2 (2022-12-09)

### Fix

- use GITHUB_OUTPUT
- align refs/tags to semantic versioning
- github deprecate set-output

## 0.1.1 (2022-12-09)

### Fix

- github action follow semantic versioning

## 0.1.0 (2022-12-09)

### Feat

- save json with timestamp
- implementation stubs
- get local ip address
- REUSE-compliant

### Fix

- missing license file
- missing contributing file
- missing dash
- synchronize env with lock file
- black version
- linter errors
- using string enum value
- TypeError, mixin must precede enum type
- linter errors
- lint stage
- disable preview workflow
- align python versions
- name key
- python 3.10, checkout action, install poetry
