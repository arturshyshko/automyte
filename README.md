# Automyte

## About

`automyte` library is designed to run automated code changes for python codebases.
It can change code for multiple projects at the same time, with minimal configuration and a bunch of built-in utils.

### Features

* `History`: Not all projects are made the same. Your tasks might fail for some of them.
Preserve the history of the runs to only target failed or new projects in subsequent re-runs.
* `VCS`: You might have some work happening in the project and don't want to disrupt it.
Integration with Git, to do all the automyte work without disrupting your local repos.
* `Config`: Configure your runs, filter files you want to work with,
use library provided tasks and utils to make your code updates as effortless as possible.


## Notes

[Updates pipeline](src/automyte/PLANS.md)
