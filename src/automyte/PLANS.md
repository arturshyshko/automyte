# Plans, Notes and Thoughts

Here's a list of things I need to remember to implement or think about:

## Common

1. Implement logging config + add and setup log messages everywhere.
1. Implement handling of random stuff (like if target_id is not present in projects)
1. add validation in automaton, to make sure all the props/tasks are correct and can be used together
  or maybe use the type guards feature in python?
1. Check for any bash command error wherever they are called and handle an error? Raise exception?

## Project,ProjectExplorer,Files,Filters

1. Add create() function in File interface + implement in OSFile
1. Add preflight_check() function to Project which is to be ran for all projects during Automaton validation phase

## Config

1. Think about adding builder setup for Config class
1. Implement typing for **kwargs for Config.get_default() (same for VCSConfig)
1. Think about reading env vars for config?
1. Think about global defaults for configs? Like, standard_worktree_path for VCS, default history file name, etc.

## VCS

1. Add support for File | Filter objects in git.add() implementation
1. Think about the whole remote validation and setup? like, I want to use remote='smth' instead of 'origin'
1. allow using stash for git, based on vcsconfig.non_disruption_strategy = 'stash' | 'worktree' ??
1. Think about running git amend? Add OnMode(amend='...', run='...') guard? It would also require to update vcs interface?
1. Think about pushing to remote, PRs and auth for them?
1. Add vcs.pr() task which will check if you have gh (or other client) installed and call them

## History

1. Use InFileHistory instance for automatons by default
1. Think about having history per task?
1. Implement CLI for managing history

## Tasks

## Future,docs,misc

1. Setup docs for the project, after done with Guards -> Breakpoint -> Config (at least)
1. Think about having AutomatonRunResult status as enum field?
    Purely for docs purpose, like "new" status means that project's never been run before.
1. Dry run???
