# Gameta

[![genius-systems](https://circleci.com/gh/genius-systems/gameta.svg?style=svg)](https://circleci.com/gh/genius-systems/gameta)

Gameta is a powerful CLI tool that helps you build workspaces to manage your 
repositories and command-line scripts. It provides powerful parameter substitution 
capabilities to customise and execute your scripts, enabling you to become more 
productive.

## What is Gameta?

Gameta is a play on the word gamete (reproductive cells), and similar to how
gametes form the building blocks for life, Gameta helps to manage the repositories 
and scripts that form the building blocks for developing more complex software. 

Gameta is build on a highly modular and extensible architecture that allows you to
customise and augment it to suit whatever your use case may be, hence the "meta" in
Gameta.

## System Requirements

Gameta requires Python 3.6+, it is designed to be multi-platform but currently is
only tested in Linux environments.

## Installation

Gameta can be easily installed and updated via pip:

```shell
$ pip install gameta  # install
$ pip install -U gameta  # update
```

## Getting Started

Getting started is really easy.

```shell
gameta init
```

Gameta will create a `.gameta` folder in the current working directory that stores
all your workspace configurations. The `.gameta` folder has the following structure:

```
.gameta
|--> .gameta  # File for storing Gameta configuration
|--> scripts  # Folder for storing Gameta scripts
|--> configs  # Folder for storing user-defined configurations
```

It will then attempt to extract relevant Version Control System (VCS) data from
all your repositories within that directory and populate the .gameta JSON file
within the `.gameta` folder.

```json
{
  "repositories": {
    "gameta": {
      "vcs": "git",
      "path": ".",
      "tags": ["metarepo"],
      "url": "https://github.com:genius-systems/gameta.git",
      "__metarepo__": true
    }
  }
}
```

If your workspace contains a `.gameta` folder and a `.gameta` JSON file, simply run
the following command to sync all linked repositories locally:

```shell
gameta sync
```

## Repository Management

Gameta aims to provide a unifying set of functionalities to manage repositories of
various kinds. It presently supports the following VCS system(s):

1. Git

For more details on the various repository management functionality, see the 
[Repository Management](https://genius-systems.github.io/gameta/user_guide/repositories/managing_repositories.md)
page.

### Adding a Repository

You should see another entry under the projects object within the .gameta file

```json
{
  "repositories": {
    "gameta": {
      "vcs": "git",
      "path": ".",
      "tags": ["metarepo"],
      "url": "git@github.com:genius-systems/gameta.git",
      "__metarepo__": true
    },
    "GitPython": {
      "vcs": "git",
      "path": "GitPython",
      "url": "https://github.com/gitpython-developers/GitPython.git",
      "__metarepo__": false
    }
  }
}
```

You should also see the repository cloned to the relative path specified.

## Command execution

Gameta provides a powerful CLI toolkit to execute commands on your repositories.
There are 2 ways this can be achieved:

1. Applying Gameta commands
2. Executing Gameta scripts

The difference between these 2 methods can be found in the 
[Commands vs Scripts](https://genius-systems.github.io/gameta/user_guide/commands/commands_vs_scripts.md)
page.

### Applying Gameta commands
Gameta commands are shell commands that support basic parameter substitution. 
These are intended for simple use-cases that do not require much command and 
parameter customisation. 

___
**Note**

Gameta commands only support the following parameter substitution methods:
1. Repository parameter substitution
2. Gameta constants substitution

See the 
[Parameter Substitution](https://genius-systems.github.io/gameta/user_guide/commands/parameter_substitution.md)
page for more details:
___

```shell
gameta apply -a -c "git fetch --all --tags --prune" -c "git merge"
```

The command above does the following to all repositories:

1. Fetches all git updates, tags and prunes redundant git artifacts.
2. Merge changes on the default branch.

Users can store Gameta commands and execute them.

```shell
# Adds a new Gameta command named 'update_source'
gameta cmd add \
  -n update_source \                              # Name of the command
  -d "Updates the source code of all projects" \  # Brief description of command
  -a \                                            # Applied to all repositories
  -c "git fetch --all --tags --prune" \           # Commands to be stored
  -c "git merge"                                  # Multi-line commands are added with multiple -c flags

# Executes this command
gameta exec -c update_source
```

See the 
[Applying Commands](https://genius-systems.github.io/gameta/user_guide/commands/applying_commands.md)
page for more information on using Gameta's command execution suite.

### Executing Gameta scripts

[Gameta Scripts](https://genius-systems.github.io/gameta/user_guide/commands/executing_scripts.md)
are the de facto way to handle complex shell operations. Coupled with Gameta's full 
[parameter substitution](https://genius-systems.github.io/gameta/user_guide/commands/parameter_substitution.md)
mechanism, Gameta Scripts are powerful execution tools to simplify a developer's 
workflow. 

Supposing one has this existing build script that builds a simple C++ programme:

```shell
#!/bin/bash

mkdir build && cd build
cmake ../ && make && make install
```

To utilise this script as a Gameta script, we must first register it:

```shell
# Register the script
gameta scripts register \
  -n build_script \         # Name of the script
  -c linux.build  \         # Category of the script
  -d "Builds on Linux" \    # A brief description of the script
  -l shell \                # Language that the script is written in
  -p current/path/to/script # Relative path where the script is currently stored
```

This will create a copy of the script in the `.gameta` folder under the scripts
folder:

```
.gameta
|--> .gameta  # File for storing Gameta configuration
|--> scripts  # Folder for storing Gameta scripts
     |--> linux
          |--> build
               |--> build_script.sh
|--> configs  # Folder for storing user-defined configurations
```

To execute this script, run the following command:

```shell
# Execute the script
gameta exec build_script
```

You can also leverage Gameta's powerful 
[parameter substitution](https://genius-systems.github.io/gameta/user_guide/commands/parameter_substitution.md)
functionality to customise the build script in the `.gameta/scripts/linux/build` 
folder for different purposes:

```shell
#!/bin/bash

mkdir build && cd build

# Update the script to accept a compiler_flags parameter
# to compile component with:
# 1. compiler_flags parameters
# 2. existing configuration stored as a Gameta constant existing_config
# 3. defaults to a standard build
cmake ../ {{ compiler_flags | existing_config | }} && make && make install
```

```shell
# Updates the Gameta script with a parameter for substitution
gameta scripts register \
  -n build_script \              # Name of the script
  -c linux.build  \              # Category of the script
  -d "Builds on Linux" \         # A brief description of the script
  -l shell \                     # Language that the script is written in
  --param compiler_flags,-DDEBUG # Registers the compiler_flags parameter with a default value

# Execute the script with user customised behaviour
gameta exec build_script -p compiler_flags=-DTEST_FLAG1,-DTEST_FLAG2

# Execute the script with default compiler_flags value (-DDEBUG)
gameta exec build_script

# Execute the script with existing_config Gameta constant value (-DDEBUG)
# If existing_config constant value does not exist, 
# then it defaults to the standard build
gameta exec build_script -p compiler_flags=None
```

## Leveraging Gameta

## Leveraging and Customising Gameta

Learn how to leverage on Gameta's capabilities in the 
[Use Cases](https://genius-systems.github.io/gameta/user_guide/applications/index.md) and  
[Best Practices](https://genius-systems.github.io/gameta/user_guide/applications/best_practices.md)
pages.

Also see the 
[Extending CLI Functionality](https://genius-systems.github.io/gameta/user_guide/customisation/extending_cli_functionality.md), 
[Adding VCS Systems](https://genius-systems.github.io/gameta/user_guide/customisation/adding_vcs_systems.md) and 
[Adding Scripting Languages](https://genius-systems.github.io/gameta/user_guide/customisation/adding_scripting_languages.md)
pages on how Gameta can be customised and extended.

## Documentation 

Documentation can be found at [Gameta Docs](https://genius-systems.github.io/gameta)
