# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.3] 2025-02-28

### Added

- v0.1.3 Update ContainsFilter to support regexp
- v0.1.3 Update Filter base class to handle logical (& | ~) operations (81d07c0)

## [0.1.2] 2025-02-28

### Changed

- v0.1.2 Fix OSFile implementation to properly process all operations (cfc7842)

## [0.1.1] 2025-02-28

### Added

- v0.1.1 Add basic readme + move updates plans to a separate file (a2076de)

### Changed

- v0.1.1 Update bash.execute util to return obj with output & status fields and capture stderr as well (3974b80)

## [0.1.0] 2025-02-28

### Added

- v0.1.0 Add a list of tasks, notes for the lib development (3503961)
- v0.1.0 Split prototype into proper folders structure (44fe56b)
- v0.1.0 Setup pure library prototype in one file with all core functionality (8fe89ab)

### Removed

- v0.0.1 Remove previous implementations of ProjectExplorer and OSFile classes (44fe56b)

## [0.0.2] 2025-02-06

### Added
- v0.0.2 Add project explorer util for interacting with all files in the project

### Changed
- v0.0.2 Only run previously failed test on test reruns to speed them up (19e04db)

## [0.0.1] 2023-05-07

### Added
- v0.0.1 Go back to hatch default build/test envs and setup automyte script (1bcdf8b)
- v0.0.1 Add changelog file + projects classifiers (c7fbe16)
- v0.0.1 Setup basic main entrypoint with smoke tests (3ae3040)
- v0.0.1 Setup basic tools + gitignore (70f1259)

### Changed
- v0.0.1 Rename package pygrate -> automyte (41e1966)
