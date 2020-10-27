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

___
**Note**
    
Bolded flags/arguments indicate that they are required, while italicised 
arguments indicate that they accept multiple arguments
___

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

Adds a new child repository to the .meta file and clone it. If the repository
is already cloned to the path provided, then extract its details and match 
them against the arguments that user provides.

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
* --clear / -c: Indicates that Gameta should also clear the local clone of 
  the repository

### gameta repo update

Updates repository details and syncs the changes locally

#### Arguments

* **--name / -n**: Name of the child repository to be updated
* --new-name / -e: New repository name to be updated to
* --new-url / -u: New repository URL to be updated to
* --new-path / -p: New local relative path within the project directory to update to
* --sync / -s: Syncs all updates physically

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

* **_--command / -c_**: Commands to be applied
* _--tags / -t_: Tagged repositories to apply commands to
* _--repositories / -r_: Names of specific repositories to apply commands to
* --shell / -s: Indicates that the command should be executed in a separate shell
* --verbose / -v: Indicates that Gameta should display the CLI output when it executes a
    command in other repositories
* --raise-errors / -e: Indicates that Gameta should terminate and raise errors that occur when
    executing commands in child repositories 

___
**Note**
   
The shell flag is required if the command to be rendered is a piped command
___

## gameta cmd

Command subcommand group, contains the following commands:

1. gameta cmd add
2. gameta cmd delete
3. gameta cmd exec

### gameta cmd add

Adds a command to the command cache within the .meta file

### gameta cmd delete

Deletes a command from the command cache

### gameta cmd exec

Executes a cached command from the command cache

[Applying Commands]: applying_commands.md