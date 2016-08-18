import click

import wavetrace.main as main
import wavetrace.utilities as ut 


CONTEXT_SETTINGS = dict(auto_envvar_prefix='WIO')

@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option()
@click.option('--product', type=click.Choice(elevation.PRODUCTS),
              default=elevation.DEFAULT_PRODUCT, show_default=True,
              help="DEM product choice.")
@click.option('--cache_dir', type=click.Path(resolve_path=True, file_okay=False),
              default=elevation.CACHE_DIR, show_default=True,
              help="Root of the DEM cache folder.")
def wio(**kwargs):
    pass
