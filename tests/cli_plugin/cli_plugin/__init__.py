import click


@click.command("test")
def test_cli() -> None:
    """
    This is a test CLI that does nothing

    Returns:
        None
    """
