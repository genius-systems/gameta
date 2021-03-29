# Applying Gameta Commands

This section introduces how Gameta applies Gameta commands over multiple 
repositories. There are 3 parts to this section:

1. Applying CLI commands directly
2. Parameter substitution for CLI and Gameta Commands
3. Using Gameta Commands

## Applying CLI Commands Directly

Gameta can be used to execute a CLI command directly with `gameta apply`. This
is useful when you want to execute CLI commands over various repositories or
configure it before execution. 

By default, Gameta applies CLI commands to only the main repository. It also 
provides the flexibility to apply them to a user-defined selection of 
registered repositories. There are 3 ways users can select repositories:

1. Applying to Tagged Repositories
2. Applying to Selected Repositories
3. Applying to All Repositories

### Applying to Tagged Repositories

Tags provide a means to group and organise your child repositories and apply CLI
commands selectively to these repositories. Supposing that one has the 
following .gameta file: 

```json
{
  "repositories": {
    "gameta": {
      "path": ".",
      "tags": ["metarepo"],
      "url": "git@github.com:genius-systems/gameta.git",
      "vcs": "git"
    },
    "GitPython": {
      "path": "GitPython",
      "tags": ["extension"],
      "url": "https://github.com/gitpython-developers/GitPython.git",
      "vcs": "git"
    },
    "gitdb": {
      "path": "core/gitdb",
      "tags": ["extension", "core"],
      "url": "https://github.com/gitpython-developers/gitdb.git",
      "vcs": "git"
    }
  }
}
```

If you only want to build the Python repositories tagged with the 'extension' tag, 
you can run the following command:

```shell
gameta apply -c "python setup.py sdist bdist_wheel" -t git
```

### Applying to Selected Repositories

Users can apply a CLI command directly to a specified set of repositories, without
needing to create tags. The same effect as described above can be achieved with
the following command:

```shell
gameta apply -c "python setup.py sdist bdist_wheel" -r GitPython -r gitdb
```

### Applying to All Repositories

Users can apply a CLI command to all repositories managed by Gameta with the 
`--all / -a` flag:

```shell
gameta apply -c "python setup.py sdist bdist_wheel" -a
```

___
**Note**

The `--all / -a` flag overrides the `--tags / -t` and `--repositories / -r` 
arguments.
___

## Parameter Substitution for CLI and Gameta Commands

CLI parameterisation is quintessential to support more complex operations. 
Gameta Commands only support 3 forms of parameter substitution:

1. *Repository Parameters*: These are unique to each repository and are 
   conventionally stored in lower case. These are added via the `gameta 
   params add` command (see [Commands]).
2. *Constants*: The same constant value is applied to all repositories and are 
   conventionally stored in upper case. These are added via the `gameta const 
   add` command (see [Commands]).
3. *Environment Variables*: These are retrieved from the environment and are 
   prefixed with a '$' e.g. $HELLO_WORLD

___
**Note**

To specify any parameter for Gameta Commands, enclose it in {curly_brackets}. The 
{branch} expression substitutes the branch parameter, the {BRANCH} expression 
substitutes the BRANCH constant and the {$BRANCH} expression substitutes the 
$BRANCH environment variable. Multiple substitutions per command are supported.
___

### Parameterising with Parameters

Consider the following .gameta file below containing the "branch" parameter that 
specifies an existing git branch:

```json
{
  "repositories": {
    "gameta": {
      "path": ".",
      "branch": "feature_a",
      "tags": ["metarepo"],
      "url": "git@github.com:genius-systems/gameta.git",
      "vcs": "git"
    },
    "GitPython": {
      "path": "GitPython",
      "branch": "master",
      "tags": ["git"],
      "url": "https://github.com/gitpython-developers/GitPython.git",
      "vcs": "git"
    },
    "gitdb": {
      "path": "core/gitdb",
      "branch": "feature_a",
      "tags": ["git", "core"],
      "url": "https://github.com/gitpython-developers/gitdb.git",
      "vcs": "git"
    }
  }
}
```

Supposing you would like to build and deploy a customised trunk configuration with code 
checked out from those branches, you can run this command below:

```bash
gameta apply -c "git checkout {branch}" -c "python setup.py bdist_wheel" -a
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

Consider the following .gameta file below that contains the PROD constant that 
specifies a branch:

```json
{
  "repositories": {
    "gameta": {
      "path": ".",
      "tags": ["metarepo"],
      "url": "git@github.com:genius-systems/gameta.git",
      "vcs": "git"
    },
    "GitPython": {
      "path": "GitPython",
      "tags": ["git"],
      "url": "https://github.com/gitpython-developers/GitPython.git",
      "vcs": "git"
    },
    "gitdb": {
      "path": "core/gitdb",
      "tags": ["git", "core"],
      "url": "https://github.com/gitpython-developers/gitdb.git",
      "vcs": "git"
    }
  },
  "constants": {
    "PROD": "master"
  }
}
```

Supposing you would like to build and deploy a production environment with code 
from the master branch specified as a constant, you can run this command below:

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

Consider the following .gameta file below:

```json
{
  "repositories": {
    "gameta": {
      "path": ".",
      "tags": ["metarepo"],
      "url": "git@github.com:genius-systems/gameta.git",
      "vcs": "git"
    },
    "GitPython": {
      "path": "GitPython",
      "tags": ["git"],
      "url": "https://github.com/gitpython-developers/GitPython.git",
      "vcs": "git"
    },
    "gitdb": {
      "path": "core/gitdb",
      "tags": ["git", "core"],
      "url": "https://github.com/gitpython-developers/gitdb.git",
      "vcs": "git"
    }
  }
}
```

Supposing you would like to build and deploy an environment with from branch 
specified via a CI/CD environment variable $BRANCH, you can run the command 
below:

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

The command below creates a Gameta command that does the following:
1. Activates the virtual environment test
2. Checks out the branch parameter for all repositories
3. Installs the Python requirements into the virtual environment test
4. Builds a Wheel distribution

```bash
gameta cmd add \
  -n build                              # Name of the command
  -c "git checkout {branch}"            # Command 1
  -c "pip install -r requirements.txt"  # Command 2
  -c "python setup.py bdist_wheel"      # Command 3
  -d "Builds wheel dist of branch"      # Brief description of the command
  -ve "test"                            # Execute with registered virtualenv test 
```

This will add the command in the previous section to the Gameta command store under
the name `hello`. 

```json
{
  "repositories": {
    "gameta": {
      "path": ".",
      "tags": [
        "metarepo"
      ],
      "url": "git@github.com:genius-systems/gameta.git",
      "vcs": "git"
    },
    "GitPython": {
      "path": "GitPython",
      "tags": [
        "git"
      ],
      "url": "https://github.com/gitpython-developers/GitPython.git",
      "vcs": "git"
    },
    "gitdb": {
      "path": "core/gitdb",
      "tags": [
        "git",
        "core"
      ],
      "url": "https://github.com/gitpython-developers/gitdb.git",
      "vcs": "git"
    }
  },
  "commands": {
    "checkout": {
      "commands": [
        "git checkout {branch}",
        "python setup.py bdist_wheel"
      ],
      "description": "",
      "all": false,
      "venv": "test",
      "tags": [],
      "repositories": [],
      "verbose": true,
      "shell": true,
      "raise_errors": true,
      "python": false
    }
  }
}
```

Run the following to invoke `hello`:

```shell
gameta exec -c hello 
``` 

Multiple Gameta commands can be stored and executed in sequence:

```shell
gameta exec -c hello -c world
```

[Commands]: ../../commands/0.3/commands.md