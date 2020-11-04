# Applying Commands

This section introduces how Gameta runs commands over multiple repositories. 
There are 3 parts to this section:

1. Applying CLI Commands
2. Parameterising CLI Commands
3. Using Gameta Commands

## Applying Commands

By default, Gameta applies CLI commands to all repositories (metarepo and all 
child repos). It also provides the flexibility to apply them to a 
user-defined selection of these repositories. There are 2 ways users can
select repositories:

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

## Parameterising Commands

CLI Commands can be customised for each repository by adding parameters (see 
[Commands]). These parameters will be substituted for a particular repository
whenever it is executed. Consider the following .meta file below containing
the "branch" parameter that specifies the a branch:

```json
{
  "projects": {
    "gameta": {
      "path": ".",
      "branch": "develop",
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

Supposing you would like to build a system with code checked out from those
branches, you can run this command below:

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

___
**Note**

To specify a parameter, enclose it in {curly_brackets}. The {branch}
expression substitutes the branch parameter; multiple substitutions
are supported.
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

Multiple Gameta commands can be executed:

```bash
gameta cmd exec -c hello -c world
```

[Commands]: commands.md