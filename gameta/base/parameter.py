from string import Template


class Parameter(Template):
    pattern = r"""
    {
        (?:(?P<escaped>\{.*\})                      |  # For escaped characters
        (?P<constructs>
            (?P<param>\$?[A-Za-z0-9_-]+)            |  # For parameters and constants
            (?P<env>__env__:(?P<env_val>.+))        |  # For explicit environment variables
            (?P<shell>__shell__:(?P<shell_val>.+))) |  # For shell commands
        (?P<or>(?&constructs)\|.+))}                   # For or logic with the final value as a default
    """

# For testing in future
"""{$TEST} {__shell__:hello} {__env__:test} {{"asdf": "hello"}} {a|fasdf} {$TEST|__bash__:hello|value} {$TEST|__bash__:hello}"""