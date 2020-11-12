# Command Reference

Like `git` the `gameta` command delegates to subcommand groups based on its
first argument. There are several subcommand groups:

1. gameta init
2. gameta sync
3. gameta repo
4. gameta tags
5. gameta params
6. gameta apply
7. gameta cmd
8. gameta const

___
**Note**
    
Bolded flags/arguments indicate that they are required, while italicised 
arguments indicate that they accept multiple arguments
___

## gameta

Main CLI group, loads .meta files and delegates subcommands to other groups

### Arguments

* --project-dir / -d: Absolute path to a metarepository, defaults to the current working 
directory
* --version / -v: Prints the current version of Gameta

## gameta init

Initialises the folder as a metarepo, searches for a .git folder and attempts
to populate the project name and Git URL from the .git folder. 

### Arguments

* --git / -g: Indicates that Gameta should initialise this folder as a git 
  repository
* --overwrite / -o: Indicates that Gameta should overwrite the existing .meta file 
  with new data

## gameta sync

Syncs all child repositories specified in the .meta file locally.

## gameta repo

Repository subcommand group, contains the following commands:

1. gameta repo add
2. gameta repo delete
3. gameta repo update
4. gameta repo ls

### gameta repo add

Adds a new child repository to the .meta file and clone it. 

___
**Note**

If the repository is already cloned to the path provided, then Gameta will 
attempt to extract its details and match them against the arguments that user
provides before adding it to the .meta file.
___

#### Arguments

* **--name / -n**: Name of the child repository to be stored
* **--url / -u**: URL of the child repository to be stored
* **--path / -p**: Relative local path within the project directory to clone the child repository to
* --overwrite / -o: Indicates that Gameta should overwrite the repository details in the .meta file
    if they exist

### gameta repo delete

Deletes an existing child repository from the .meta file and its local clone.

#### Arguments

* **--name / -n**: Name of the child repository to be deleted
* --no-clear / -c: Indicates that Gameta should not clear the local clone of the repository

### gameta repo update

Updates repository details and syncs the changes locally

#### Arguments

* **--name / -n**: Name of the child repository to be updated
* --new-name / -e: New repository name to be updated to
* --new-url / -u: New repository URL to be updated to
* --new-path / -p: New local relative path within the project directory to update to
* --no-sync / -s: Does not apply updates locally

### gameta repo ls

Lists all repositories added

## gameta tags

Tags subcommand group, contains the following commands:

1. gameta tags add
2. gameta tags delete

### gameta tags add

Adds/updates tags of a particular repository.

#### Arguments

* **--name / -n**: Name of the child repository to add tags to
* **_--tags / -t_**: Tags to be added to the child repository

### gameta tags delete

Deletes selected tags from a particular repository.

___
**Note**

The "metarepo" tag of the metarepo cannot be deleted 
___

#### Arguments

* **--name / -n**: Name of the child repository to delete tags from
* **_--tags / -t_**: Tags to be deleted from the child repository

## gameta params

Parameters subcommand group, contains the following commands:

1. gameta params add
2. gameta params delete

### gameta params add

Adds a new set of parameters to all repositories, this can be done in 2 ways:

1. User-prompt for each repository (default)
2. Providing a default value that will be applied to all repositories

___
**Note**

If users choose a dict/list parameter types, then they need to input their
parameter values as JSON decodable strings e.g. `'{"hello": "world"}'` or
`'["hello", "world"]'`
___

___
**Note**
   
From version [0.2.3](https://pypi.org/project/gameta/0.2.3/), environment variables
parameters are acceptable parameter values. These parameter values will be substituted
by the appropriate environment variables. For example the following `gameta params` 
command below is acceptable:

```bash
gameta params add -p branch -y -v '${BITBUCKET_BRANCH}'
```

This will result in the configuration below:

```JSON
{
  "projects": {
    "gameta": {
      "path": ".",
      "tags": ["metarepo"],
      "url": "https://github.com:genius-systems/gameta.git",
      "branch": "${BITBUCKET_BRANCH}"
    }
  }
}
```

And the branch parameter for gameta will be resolved to the `${BITBUCKET_BRANCH}` 
environment variable
___

#### Arguments

* **--param / -p**: Name of the parameter to be added to each repository
* --type / -t: Parameter type to be added for each repository, users can only choose one
    of the following: int, float, str (default), bool, dict, list
* --value / -v: Default value to be added for each repository in the event users input an
    invalid command when prompted or skip prompt entirely. Defaults to None
* --skip-prompt / -y: Skips user prompt and adds the default value to all parameter fields

### gameta params delete

Deletes a parameter set from all repositories.

#### Arguments
 
* **--param / -p**: Name of the parameter to be deleted

## gameta apply

Applies a set of CLI commands to a specified set of repositories (see 
[Applying Commands])

### Arguments

* **_--command / -c_**: CLI commands to be applied
* _--tags / -t_: Tagged repositories to apply CLI commands to
* _--repositories / -r_: Names of specific repositories to apply CLI commands to
* --shell / -s: Indicates that the CLI commands should be executed in a separate shell
* --python / -p: Indicates that the commands are Python scripts and should be executed 
with the Python 3 interpreter
* --verbose / -v: Indicates that Gameta should display the CLI output when it executes a
    CLI command in other repositories
* --raise-errors / -e: Indicates that Gameta should terminate and raise errors that occur
    when executing CLI commands in child repositories 

___
**Note**
   
The shell flag is required if the CLI command to be rendered is a piped CLI command
or if the `cd` command is used. It will also be automatically added if multiple CLI
commands are provided.
___

___
**Note**
   
Python scripts are entered as is, use `''` to help enter multi-line Python scripts and
handle imports. This approach also works for more complex shell scripts. An example is
provided below.
```
gameta apply -p -c '
from os import getcwd
print(getcwd())
'
```
___

___
**Note**
   
A special variable **\_\_repos\_\_** is reserved to provide access to repository details
when using Python scripts. This variable should **only be used in Python scripts** as 
it causes issues when substituted into shell parameters.
___

## gameta cmd

Command subcommand group, contains the following commands:

1. gameta cmd add
2. gameta cmd delete
3. gameta cmd update
4. gameta cmd ls
5. gameta cmd exec

### gameta cmd add

Adds a Gameta command to the Gameta command store within the .meta file

___
**Note**

A Gameta command is a `gameta apply` command consisting of a set of CLI commands, tags, 
repositories and flags (shell, python, verbose, raise errors) that control its execution
___

___
**Note**
   
If the Python flag is entered, Gameta will check if the Python scripts entered are valid.
All commands **must** be Python scripts if the Python flag is used.
___

#### Arguments 
* **--name / -n**: Name 
* --overwrite / -o: Indicates that Gameta should overwrite the existing .meta file 
    with new data
* **_--command / -c_**: CLI commands to be applied
* _--tags / -t_: Tagged repositories to apply CLI commands to
* _--repositories / -r_: Names of specific repositories to apply CLI commands to
* --shell / -s: Indicates that the CLI command should be executed in a separate shell
* --python / -p: Indicates that the commands are Python scripts and should be executed 
with the Python 3 interpreter
* --verbose / -v: Indicates that Gameta should display the CLI output when it executes a
    CLI command in other repositories
* --raise-errors / -e: Indicates that Gameta should terminate and raise errors that occur when
    executing CLI commands in child repositories 

### gameta cmd delete

Deletes a Gameta command from the Gameta command store

#### Arguments
* **--name / -n**: Name of the Gameta command to be deleted

### gameta cmd update

Updates a Gameta command that exists in the Gameta command store

___
**Note**
   
If the Python flag is set, Gameta will check if the Python scripts entered are valid.
If the Python flag is unset, Gameta will check that all the CLI commands are not Python
compilable.
___

#### Arguments
* **--name / -n**: Gameta command name to be updated
* _--command / -c_: New CLI commands to be executed
* _--tags / -t_: New repository tags apply CLI commands to
* _--repositories / -r_: New repositories to apply CLI commands to
* --verbose / -v: Display execution output when CLI commands are applied
* --no-verbose / -nv: Do not display execution output when CLI commands are applied
* --shell / -s: Execute CLI commands in a separate shell
* --no-shell / -ns: Do not execute CLI commands in a separate shell
* --python / -p: Execute as Python scripts with the Python 3 interpreter
* --no-python / -np: Do not execute as Python scripts
* --no-shell / -ns: Do not execute CLI commands in a separate shell
* --raise-errors / -e: Raise errors that occur when CLI commands are executed and 
    terminate
* --no-errors / -ne: Do not raise errors that occur when CLI commands are executed 
    and terminate

### gameta cmd ls

Lists all existing Gameta commands in the Gameta command store

### gameta cmd exec

Executes a sequence of Gameta commands from the command store

#### Arguments
* **_--commands / -c_**: Gameta commands to be executed

## gameta const

Constants subcommand group, contains the following commands:

1. gameta const add
2. gameta const delete

### gameta const add

Adds/Updates constants in the constants store

___
**Note**
   
Constants are applied consistently across all repositories, while parameters are unique
to each repository. Hence to distinguish between parameters which are unique, constants
are all converted to uppercase.
___

___
**Note**
   
From version [0.2.3](https://pypi.org/project/gameta/0.2.3/), constants can be added 
with a '$' symbol e.g. `$BRANCH`. These constants will be automatically substituted
the corresponding environment variables extracted from the environment i.e. the 
resultant substitution from the constant store and run-time environment configuration
below is `world`.

```JSON
{
  "constants": {
    "$BRANCH": "hello"
  }
}
``` 

```bash
export BRANCH=world
```
___

### Arguments
* **--name / -n**: Name of the Gameta constant to be added
* **--type / -t**: Type of the Gameta constant (int, float, bool and str) to be added
* **--value / -v**: Value of the Gameta constant to be added

___
**Note**
   
Gameta constants only support basic types, these will be used to interpret the 
constant value that the user inputs. Hence the type has to be one of the 4 types 
below:

1. *int*: Integer
2. *float*: Floating Point
3. *bool*: Boolean
4. *str*: String
___

### gameta const delete

Deletes an existing constant from the constants store

### Arguments
* **--name / -n**: Name of the Gameta constant to be deleted
___
**Note**
   
The constant name can be provided in either lowercase or uppercase.
___

[Applying Commands]: ../../user_guide/applying_commands.md