import typer

from evalitai import __version__

app = typer.Typer(
    name="evalitai",
    help="Evalitai engine: compare candidate vs baseline LLM outputs, offline.",
    no_args_is_help=True,
)


@app.callback()
def main() -> None:
    """Evalitai engine CLI."""


@app.command()
def version() -> None:
    """Print the installed evalitai-engine version."""
    typer.echo(__version__)


if __name__ == "__main__":
    app()
