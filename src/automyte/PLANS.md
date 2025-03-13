# Plans, Notes and Thoughts

Here's a list of things I need to remember to implement or think about:

## Common

1. Implement logging config + add and setup log messages everywhere.
1. Implement handling of random stuff (like if target_id is not present in projects)
1. Add util for reading paths from a separate file?
  * Useful for when ran across different machines by multiple people.
1. Maybe update WithFlagsMixin class that would implement following stuff?
  * if self.default_flags -> self.flags = self.default_flags + self.flags? need to think about this one more.
  * use it for VCS implementations?

## Project,ProjectExplorer,Files,Filters

1. Add create() function in File interface + implement in OSFile
1. Modify ignore_locations implementation to:
  * Maybe use .gitignore and other vcs available files?
  * Allow configuring this in Config?

## Config

1. Think about adding builder setup for Config class
1. Implement typing for **kwargs for Config.get_default() (same for VCSConfig)
1. Think about reading env vars for config?
1. Think about global defaults for configs? Like, standard_worktree_path for VCS, default history file name, etc.

## VCS

1. Check if can make vcs.add() return status='skipped' if no files were added? possible implementation would be:
  * `if hasattr(ctx.vcs, 'add'): return ctx.vcs.add() else ctx.run('add').flags(...)`
    this way, can rely on specific vcs implementations but they remain optional
  * If vcs.add() can skip - vcs.commit() can be wrapped with
    `flow.If(check=guards.PREVIOUS_TASK.is_success, vcs.commit('...'))`
1. Think about the whole remote validation and setup? like, I want to use remote='smth' instead of 'origin'
1. Add vcs.pr() task which will check if you have gh (or other client) installed and call them
1. allow using stash for git, based on vcsconfig.non_disruption_strategy = 'stash' | 'worktree' ??
1. Add support for File | Filter objects in git.add() implementation

## History

1. Use InFileHistory instance for automatons by default
1. Think about having history per task? This would require 3 things:
  * utils.WithID(id='...', task)
  * additional field stored in status (`last_task`).
  * in TasksFlow, to skip all the tasks, until task with given ID is met and start running from there based on settings
  * This can be a bit tricky with container tasks? (as it will be skipped by default then)
    Might have to rely on smth like `if hasattr(task, 'is_container')` which will have to be implemented by guards and stuff
1. Implement CLI for managing history

## Tasks

1. Allow for `initializers` section in TasksFlow, which runs even before in_working_state()?? Treat with CAUTION!
1. Think on allowing to setup post/pre tasks in array form of TasksFlow automaton initialization?
  * Either plain python object syntax
  * or maybe `flow.Postprocess()` and `flow.Preprocess()`?
    That might require either implementing `call_once` treat or some `TasksFlow.arrange_tasks()` (or `prepare`) method?
    this might in turn require checking task containers implementation
1. Review Breakpoint implementation once again (read todo of the class, but don't treat it as final idea)


## Future,docs,misc

1. Setup docs for the project, after done with Guards -> Breakpoint -> Config (at least)
1. Think about having AutomatonRunResult status as enum field?
    Purely for docs purpose, like "new" status means that project's never been run before.
1. Dry run???

## Notes for myself

1. See if should use github releases or just tags or both
1. Check how to setup proper docs
  * the ones used for hatchling or maybe use backstage?
  * see if should use docstrings per class or separate docstring for contributors and separate docs for usage?
  * Use https://github.com/mkdocs/mkdocs + github pages
1. When writing docs for examples - for simplest case, remember saying:
  * "this simple example highlights couple of essential mechanics of automyte lib: ..."
  and mention the flushing() mechanics, etc.

1. Check if want to setup `hatch release` command that would:
  * run tests for ALL? python versions
  * tag commit / mark github release
  * build -> publish -> push tags/release to github
1. Setup CI/CD pipeline that would basically do the same as `hatch release` command, but:
  * Only do release parts of this on merge to master if version has changed
  * run tests for all python versions on PR level
  * update test coverage and maybe publish new docs and stuff?
