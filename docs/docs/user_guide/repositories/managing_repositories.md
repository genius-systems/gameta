# Managing Repositories

This section describes how you can use Gameta to manage your repositories of 
various types. There are 3 parts to this section:

1. Multi-VCS support
2. Initialising local repositories
3. Managing repositories

## Multi-VCS Support

Gameta provides a generic abstraction interface for various VCS. VCS that are 
presently supported are indicated in bold, while those with plans to be supported 
are indicated in italics:

1. **Git**
2. *Mercurial*
3. *SVN*

Gameta will automatically detect the underlying VCS type during execution, and 
uses the appropriate interfaces to handle each VCS type. However, the tradeoff 
for such convenience is a standardised set of operations that are common across 
most VCS types. You can utilise Gameta commands or Gameta scripts to augment the
supported operations. 

## Initialising Local Repositories

Gameta provides functionality to initialise local repositories. This can be done
with the command below:

```shell
gameta repo init
```

You will have to update the repository URL manually later with the following 
command:

```shell
gameta repo update -u "http://url/of/repo"
```

---
**Note**

An error will be raised if the VCS does not provide local repository 
initialisation functionality i.e. Centralised VCS like SVN
---

## Managing Repositories

Gameta provides the standard CRUD operations for managing repositories. On top 
of these, Gameta also provides other common VCS operations so users can handle 
basic VCS workflows with Gameta. The following commands illustrates a VCS workflow
handled by Gameta:

```shell
# Lists all available branches
gameta repo branch ls

# Switches to a particular branch
gameta repo branch test_branch

# Updates the current branch with changes
gameta repo update

# Shows the status of the repository
gameta repo status 

# Adds a commit
gameta repo commit -m "Commit message"

# Pushes changes 
gameta repo push

# Deletes a particular branch
gameta repo branch delete test_branch
```

All of these functionalities are housed under the `gameta repo` command group, see
[Commands] for the full set of repository management operations.

[Commands]: ../../commands/0.3/commands.md