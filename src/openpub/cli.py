import click

from openpub.init_cmd import run_init
from openpub.verify_cmd import run_verify


@click.group()
def cli():
    """openpub — verify scientific paper claims with code."""
    pass


@cli.command()
@click.argument("claims_json", type=click.Path(exists=True))
@click.option("-o", "--output", default=".", help="Output directory for scaffolded project.")
def init(claims_json, output):
    """Scaffold a paper verification project from a claims JSON file."""
    run_init(claims_json, output)
    click.echo(f"Scaffolded project in {output}")


@cli.command()
@click.option("--claims", default="./claims.json", help="Path to claims JSON file.")
@click.option("--dir", "directory", default=".", help="Directory to scan for .py files.")
def verify(claims, directory):
    """Run @claim-decorated functions and compare results against expected values."""
    exit_code = run_verify(claims, directory)
    raise SystemExit(exit_code)
