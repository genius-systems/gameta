# Applying Commands

This section introduces how Gameta runs commands over multiple repositories. 
There are 3 parts to this section:

1. Applying CLI Commands
2. Applying Python Commands
3. Parameterising CLI Commands
4. Using Gameta Commands

## Applying Commands

By default, Gameta applies CLI commands to all repositories (metarepo and all 
child repos). It also provides the flexibility to apply them to a user-defined
selection of these repositories. There are 2 ways users can select repositories:

1. Applying to Tagged Repositories
2. Applying to Selected Repositories

### Applying to Tagged Repositories

Tags provide a means to group and organise your child repositories and apply CLI
commands selectively to these repositories. Supposing that one has the 
following .meta file: 

```json
{
  "projects": {
    "gameta": {
      "path": ".",
      "tags": ["metarepo"],
      "url": "git@github.com:genius-systems/gameta.git"
    },
    "GitPython": {
      "path": "GitPython",
      "tags": ["git"],
      "url": "https://github.com/gitpython-developers/GitPython.git"
    },
    "gitdb": {
      "path": "core/gitdb",
      "tags": ["git", "core"],
      "url": "https://github.com/gitpython-developers/gitdb.git"
    }
  }
}
```

If you only want to build the Python repositories tagged with git, you can
run the following command:

```bash
gameta apply -c "python setup.py sdist bdist_wheel" -t git
```

### Applying to Selected Repositories

Users can apply a CLI command directly to a specified set of repositories, without
needing to create tags. The same effect as described above can be achieved with
the following command:

```bash
gameta apply -c "python setup.py sdist bdist_wheel" -r GitPython -r gitdb
```

## Applying Python Commands

From version [0.2.2](https://pypi.org/project/gameta/0.2.1/), Gameta can apply Python 3 
scripts across various repositories. This provides users with the flexibility to augment 
their CLI operations with Python scripts. Python scripts are entered similar to multi-line
shell commands using the `''`. Consider the Python script below that:

1. Generates an encryption key of configurable length (using the KEY_LEN constant) 
consisting of only ASCII variables
2. Writes the key to all repositories (using the reserved __repo__ variable) to a 
configurable file name (using the ENCRYPTION_FILE_NAME constant)

```bash
gameta apply -p -c '
from os import getcwd
from random import choice
from string import ascii_lowercase, ascii_uppercase, digits, punctuation
key = "".join([choice(ascii_lowercase + ascii_uppercase + digits + punctuation) for _ in range({KEY_LEN})])
for repo, details in {__repos__}.items():
    with open(join(getcwd(), details["path"], "{ENCRYPTION_FILE_NAME}"), "w") as f:
        f.write(key)
' -r main_repo
```

___
**Note**

If the `--python` / `-p` flag is used, all commands entered (with the `-c` parameter) in
the same execution **must** be Python scripts.
___

___
**Note**

When writing Python scripts, use double quotes for all Python strings in the script as 
issues may arise when the command is applied due to string escaping.
___

## Parameterising Commands

CLI parameterisation is quintessential to support more complex operations. There are 3 
types of parameters that can be substituted:

1. *Parameters*: These are unique to each repository and are conventionally stored in
lower case. These are added via the `gameta params add` command (see [Commands]).
2. *Constants*: The same constant value is applied to all repositories and are 
conventionally stored in upper case. These are added via the `gameta const add` command
(see [Commands]).
3. *Environment Variables*: These are retrieved from the environment and are prefixed
with a '$' e.g. $HELLO_WORLD

___
**Note**

To specify any parameter, enclose it in {curly_brackets}. The {branch} expression 
substitutes the branch parameter, the {BRANCH} expression substitutes the BRANCH 
constant and the {$BRANCH} expression substitutes the $BRANCH environment variable.
Multiple substitutions per command are supported.
___

### Parameterising with Parameters

Consider the following .meta file below containing the "branch" parameter that specifies
an existing git branch:

```json
{
  "projects": {
    "gameta": {
      "path": ".",
      "branch": "feature_a",
      "tags": ["metarepo"],
      "url": "git@github.com:genius-systems/gameta.git"
    },
    "GitPython": {
      "path": "GitPython",
      "branch": "master",
      "tags": ["git"],
      "url": "https://github.com/gitpython-developers/GitPython.git"
    },
    "gitdb": {
      "path": "core/gitdb",
      "branch": "feature_a",
      "tags": ["git", "core"],
      "url": "https://github.com/gitpython-developers/gitdb.git"
    }
  }
}
```

Supposing you would like to build and deploy a customised trunk configuration with code 
checked out from those branches, you can run this command below:

```bash
gameta apply -c "git checkout {branch}" -c "python setup.py bdist_wheel"
```

This is the same as running the following bash commands:
```bash
# To build gameta
git checkout develop && python setup.py bdist_wheel

# To build GitPython
cd GitPython && git checkout master && python setup.py bdist_wheel && cd ..

# To build gitdb
cd core/gitdb && git checkout feature_a && python setup.py bdist_wheel && cd ../..
```

### Parameterising with Constants

Consider the following .meta file below that contains the BRANCH constant that specifies
a branch:

```json
{
  "projects": {
    "gameta": {
      "path": ".",
      "tags": ["metarepo"],
      "url": "git@github.com:genius-systems/gameta.git"
    },
    "GitPython": {
      "path": "GitPython",
      "tags": ["git"],
      "url": "https://github.com/gitpython-developers/GitPython.git"
    },
    "gitdb": {
      "path": "core/gitdb",
      "tags": ["git", "core"],
      "url": "https://github.com/gitpython-developers/gitdb.git"
    }
  },
  "constants": {
    "PROD": "master"
  }
}
```

Supposing you would like to build and deploy a production environment with code from the
master branch specified as a constant, you can run this command below:

```bash
gameta apply -c "git checkout {PROD}" -c "python setup.py bdist_wheel"
```

This is the same as running the following bash commands:
```bash
# To build gameta
git checkout master && python setup.py bdist_wheel

# To build GitPython
cd GitPython && git checkout master && python setup.py bdist_wheel && cd ..

# To build gitdb
cd core/gitdb && git checkout master && python setup.py bdist_wheel && cd ../..
```

### Parameterising with Environment Variables

Consider the following .meta file below:

```json
{
  "projects": {
    "gameta": {
      "path": ".",
      "tags": ["metarepo"],
      "url": "git@github.com:genius-systems/gameta.git"
    },
    "GitPython": {
      "path": "GitPython",
      "tags": ["git"],
      "url": "https://github.com/gitpython-developers/GitPython.git"
    },
    "gitdb": {
      "path": "core/gitdb",
      "tags": ["git", "core"],
      "url": "https://github.com/gitpython-developers/gitdb.git"
    }
  }
}
```

Supposing you would like to build and deploy an environment with from branch specified
via a CI/CD environment variable $BRANCH, you can run the command below:

```bash
gameta apply -c "git checkout {$BRANCH}" -c "python setup.py bdist_wheel"
```

This is the same as running the following bash commands:
```bash
# To build gameta
git checkout $BRANCH && python setup.py bdist_wheel

# To build GitPython
cd GitPython && git checkout $BRANCH && python setup.py bdist_wheel && cd ..

# To build gitdb
cd core/gitdb && git checkout $BRANCH && python setup.py bdist_wheel && cd ../..
```

___
**Note**

When parameterising environment variables, use single quotes instead of double quotes
to prevent the shell from automatically expanding these variables.
```bash
gameta apply -c 'git checkout {$BRANCH}'  # This is recommended
gameta apply -c "git checkout {$BRANCH}"  # Shell will attempt to substitute $BRANCH
```
___


## Using Gameta Commands

Gameta commands are an abstraction of CLI commands applied with `gameta apply`,
hence a Gameta command consists of all the parameters the `gameta apply` command 
i.e. CLI commands, tags, repositories, shell, verbose and raise errors. They 
simplify the `gameta apply` interface, allowing you to store commonly used commands
and reuse them.

To create a Gameta command, run the following:

```bash
gameta cmd add -n hello -c "git checkout {branch}" -c "python setup.py bdist_wheel"
```

This will add the command in the previous section to the Gameta command store under
the name `hello` and run the following to invoke `hello`:

```bash
gameta cmd exec -c hello 
``` 

Multiple Gameta commands can be stored and executed in sequence:

```bash
gameta cmd exec -c hello -c world
```

[Commands]: ../commands/0.2/commands.md