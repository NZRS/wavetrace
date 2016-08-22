wavetrace Package
======================

The ``wavetrace`` package contains four modules that depend on each other like this::

    main -> constants, utilities
    utilities -> constants
    cli -> main, utilities, constants

    
main Module
-------------------------------------

.. automodule:: wavetrace.main
    :members:
    :undoc-members:
    :show-inheritance:


utilities Module
---------------------------

.. automodule:: wavetrace.utilities
    :members:
    :undoc-members:
    :show-inheritance:


constants Module
---------------------------

.. automodule:: wavetrace.constants
    :members:
    :undoc-members:
    :show-inheritance:


cli Module
---------------------------
Sphinx auto-documentation does not work on this module, because all the functions inside are decorated by Click decorators, which don't play nicely with Sphinx.
So use the command line to access the documentation for Wavey, the command line interface for Wavetrace:

.. code-block:: shell

    wavey --help
    Usage: wavey [OPTIONS] COMMAND [ARGS]...

    Options:
      --help  Show this message and exit.

    Commands:
      compute_coverage      Compute radio signal coverage reports
      compute_tile_ids      Compute SRTM tiles IDs needed
      download_topography   Download topography data (SRTM)
      process_topography    Process topography data (SRTM)
      process_transmitters  Process transmitter data (CSV)
      srtm_nz               Print the SRTM tiles that cover New Zealand

.. automodule:: wavetrace.cli
    :members:
    :undoc-members:
    :show-inheritance:


