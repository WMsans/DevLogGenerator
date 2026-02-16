import typer

app = typer.Typer(help="Generate video dev logs from git history.")


@app.command()
def init():
    """Phase 1: Scan git history and generate draft.md."""
    typer.echo("init: not implemented")


@app.command()
def expand():
    """Phase 2: Expand {{EXPAND}} tags in draft.md into script.md."""
    typer.echo("expand: not implemented")


@app.command()
def render():
    """Phase 3: Render script.md into devlog.mp4."""
    typer.echo("render: not implemented")


if __name__ == "__main__":
    app()