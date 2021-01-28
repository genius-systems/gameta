# Release Notes

## Upgrading

To upgrade Gameta to the latest version, use pip:

```bash
pip install -U gameta
```

You can determine your currently installed version using `gameta --version`:

```bash
gameta --version
```

## Maintenance team

The current members of the Gameta team.

* [@darkvariantdivine](https://github.com/darkvariantdivine/)

## Version 0.2.6 (2021-01-28)

* Hotfixes for various issues:
  * Improving print statements from commands executed [link](https://github.com/genius-systems/gameta/issues/43)

## Version 0.2.5 (2020-11-16)

* Hotfixes for various issues:
  * Description parameter affects `gameta cmd exec`

## Version 0.2.4 (2020-11-16)

* Adding support for Python 3.6 [link](https://github.com/genius-systems/gameta/issues/27)
* Adding description to Gameta commands [link](https://github.com/genius-systems/gameta/issues/30)

## Version 0.2.3 (2020-11-13)

* Added environment variable substitution for parameters and constants
[link](https://github.com/genius-systems/gameta/issues/24)

## Version 0.2.2 (2020-11-11)

* Added Python 3 script execution functionality to `gameta apply` [link](https://github.com/genius-systems/gameta/issues/20)
* Added Python 3 script execution functionality to `gameta cmd` [link](https://github.com/genius-systems/gameta/issues/20)
* Updated documentation and README.md

## Version 0.2.1 (2020-11-10)

* Hot fixes for various issues:
  * Fixing bug where `gameta init` clears the entire .gitignore file [link](https://github.com/genius-systems/gameta/issues/10)
  * Improving documentation

## Version 0.2.0 (2020-11-10)

* Added functionality to extract and substitute environment variables [link](https://github.com/genius-systems/gameta/issues/16)
* Added functionality to add, delete and substitute constants [link](https://github.com/genius-systems/gameta/issues/16)
* Added functionality to print the current version of Gameta
* Added functionality to validate .meta file contents against a JSON Schema
* Updated documentation to present different CLI versions of Gameta
* Pretty print JSON output to .meta file [link](https://github.com/genius-systems/gameta/issues/17)

## Version 0.1.1 (2020-11-5) (Deprecated by 2021-1-1)

* Hot fixes for various issues:
  * Handling of malformed .meta files [link](https://github.com/genius-systems/gameta/issues/13)
  * Params subgroup was not added [link](https://github.com/genius-systems/gameta/issues/11)
  * .gitignore was cleared when repos are added [link](https://github.com/genius-systems/gameta/issues/10)
  * `gameta sync` throws error if repos are already present [link](https://github.com/genius-systems/gameta/issues/9)
      
## Version 0.1.0 (2020-10-30) (Deprecated by 2021-1-1)

* Added init command to initialise an empty repository
* Added the sync command to sync changes locally
* Added the repo CLI commands to add, delete, update and list repositories
* Added the tags CLI commands to add and delete repository tags
* Added the params CLI commands to add and delete repository parameters
* Added the cmd CLI commands to add, delete, update, list and execute Gameta commands
