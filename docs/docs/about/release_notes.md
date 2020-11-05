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

## Version 0.1.1 (2020-11-5)

* Hot fixes for various issues:
  * Handling of malformed .meta files [link](https://github.com/genius-systems/gameta/issues/13)
  * Params subgroup was not added [link](https://github.com/genius-systems/gameta/issues/11)
  * .gitignore was cleared when repos are added [link](https://github.com/genius-systems/gameta/issues/10)
  * `gameta sync` throws error if repos are already present [link](https://github.com/genius-systems/gameta/issues/9)
      
## Version 0.1.0 (2020-10-30)

* Added init command to initialise an empty repository
* Added the sync command to sync changes locally
* Added the repo CLI commands to add, delete, update and list repositories
* Added the tags CLI commands to add and delete repository tags
* Added the params CLI commands to add and delete repository parameters
* Added the cmd CLI commands to add, delete, update, list and execute Gameta commands
