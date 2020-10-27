# Applying Commands

This section introduces how Gameta runs commands over multiple repositories. 
There are 2 parts to this section:

1. Applying Commands
2. Parameterising Commands

## Applying Commands

By default, Gameta applies commands to all repositories (metarepo and all 
child repos). It also provides the flexibility to apply them to a 
user-defined selection of these repositories. There are 2 ways users can
select repositories:

1. Applying to Tagged Repositories
2. Applying to Selected Repositories

### Applying to Tagged Repositories

Tags provide a means to group and organise your child repositories and apply
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

Users can apply a command directly to a specified set of repositories, without
needing to create tags. The same effect as described above can be achieved with
the following command:

```bash
gameta apply -c "python setup.py sdist bdist_wheel" -r GitPython -r gitdb
```

## Parameterising Commands

Commands can be customised for each repository by adding parameters (see 
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

!!! note

    To specify a parameter, enclose it in {curly_brackets}. The {branch}
    expression substitutes the branch parameter; multiple substitutions
    are supported.

[Commands]: user_guide/commands.md