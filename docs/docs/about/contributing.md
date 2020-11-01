# Contributing to Gameta

Gameta welcomes, and depends, on contributions from developers and users in
the open source community. Contributions can be made in a number of ways, a
few examples are:

- Code patches via pull requests
- Documentation improvements
- Bug reports and patch reviews

## Code of Conduct

Everyone interacting in the Gameta's codebases, issue trackers, chat
rooms, and mailing lists is expected to follow the [PyPA Code of Conduct].

## Reporting an Issue

Please include as much detail as you can. Let us know your platform and 
Gameta version. If you get an error please include the full error and 
traceback.

## Testing the Development Version

If you want to just install and try out the latest development version of
Gameta you can do so with the following command. This can be useful if you
want to provide feedback for a new feature or want to confirm if a bug you
have encountered is fixed in the git master. It is **strongly** recommended
that you do this within a [virtualenv].

```bash
pip install git+https://github.com/genius-systems/gameta.git@master
```

## Installing for Development

First you'll need to fork and clone the repository. Once you have a local
copy, run the following command. It is **strongly** recommended that you do
this within a [virtualenv].

```bash
pip install --editable .
```

This will install Gameta in development mode which binds the `gameta` command
to the git repository.

## Running the tests

To run the tests, it is recommended that you use [tox].

Install Tox using [pip] by running the command `pip install tox`.
Then the test suite can be run with the command `tox` in the
root of your Gameta repository.

It will attempt to run the tests against all of the Python versions we 
support. So don't be concerned if you are missing some and they fail. 
The rest will be verified when you submit a pull request.

## Submitting Pull Requests

Once you are happy with your changes or you are ready for some feedback, push
it to your fork and send a pull request. For a change to be accepted it will
most likely need to have tests and documentation if it is a new feature.

[virtualenv]: https://virtualenv.pypa.io/en/latest/user_guide.html
[pip]: https://pip.pypa.io/en/stable/
[tox]: https://tox.readthedocs.io/en/latest/
[PyPA Code of Conduct]: https://www.pypa.io/en/latest/code-of-conduct/
