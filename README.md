## Notes

Here's a list of things I need to remember to implement or think about:

### Common

1. Write a proper bash execute function, which will handle/report errors and properly process string cmd
1. Implement logging config + add and setup log messages everywhere.
1. Implement handling of random stuff (like if target_id is not present in projects)
1. add validation in automaton, to make sure all the props/tasks are correct and can be used together
  or maybe use the type guards feature in python?


### Project,ProjectExplorer,Files,Filters

1. Make sure OSFile implementation properly handles files move/delete, content override
1. Implement BaseFilter class which allows combining filters conditions via "&", "|", ... operators

1. Think about contains filter with regexp? Current file interface doesn't support contains with regexp.

### Config

1. Think about adding builder setup for Config class
1. Implement typing for **kwargs for Config.get_default() (same for VCSConfig)
1. Think about reading env vars for config?
1. Think about global defaults for configs? Like, standard_worktree_path for VCS, etc.

### VCS

1. Update whole Git implementation
1. Handle situation when requested branch already exists for worktree?
1. Think about pushing to remote, PRs and auth for them?
1. allow using stash for git, based on vcsconfig.non_disruption_strategy = 'stash' | 'worktree' ??
1. Think about running git amend? Add OnMode(amend='...', run='...') guard? It would also require to update vcs interface?

### History

1. Implement splitting history per automaton
1. Think about having history per task?

### Guards

1. Think again about guards implementation, not exatly the fan of a base class
1. Think about typing for guards
1. Add ActOn task guard which accepts filters to filter files further? Like:
  ActOn(filter_by: Filter, tasks=...)
1. TaskGuard to (only run if "run" mode for example)
  or if branches, some conditions, whatever - just some built-in util class

### Future,docs,misc

1. Think about having AutomatonRunResult status as enum field?
    Purely for docs purpose, like "new" status means that project's never been run before.
1. Dry run???
