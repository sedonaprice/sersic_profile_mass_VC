***************************************************************************
Non-spherical deprojected Sérsic mass profiles and circular velocity curves
***************************************************************************

.. image:: http://img.shields.io/badge/powered%20by-AstroPy-orange.svg?style=flat
    :target: http://www.astropy.org
    :alt: Powered by Astropy Badge


Description
###########
Package to calculate various profiles for deprojected, flattened (or elongated)
Sérsic mass distributions, including:
enclosed mass, circular velocity, density, log density slope, surface density,
and projected enclosed mass.

These calculations follow and extend the derivation of rotation curves for flattened
Sérsic bulges presented by `Noordermeer, 2008, MNRAS, 385, 1359`_.
Further details about the calculations included in this package
are described in `Price et al., 2022, A&A 665 A159`_.

.. _Noordermeer, 2008, MNRAS, 385, 1359: https://ui.adsabs.harvard.edu/abs/2008MNRAS.385.1359N/abstract
.. _Price et al., 2022, A&A 665 A159: https://ui.adsabs.harvard.edu/abs/2022A%26A...665A.159P/abstract

Please see `the documentation`_ for this package for detailed information about installation,
usage, and to `download`_ the set of pre-computed Sérsic profile tables.

.. _the documentation: https://sedonaprice.github.io/deprojected_sersic_models/
.. _download: https://sedonaprice.github.io/deprojected_sersic_models/downloads.html

Usage
#####

.. code-block:: python

    import os
    import numpy as np
    import deprojected_sersic_models as deproj_sersic
    table_dir = os.getenv('DEPROJECTED_SERSIC_MODELS_DATADIR')

    # Sersic profile properties & radius array
    total_mass = 1.e11
    Reff = 5.0
    n = 1.0
    invq = 5.    # Oblate, q = c/a = 0.2

    r = np.arange(0., 30.1, 0.1)

    # Load & interpolate all profiles in saved table:
    table_interp = deproj_sersic.interpolate_entire_table(r=r, total_mass=total_mass,
                                                          Reff=Reff, n=n, invq=invq,
                                                          path=table_dir)


Dependencies
############
* numpy
* scipy
* matplotlib
* astropy
* dill


Acknowledgement
###############
If you use this package or the precomputed profile tables in a publication,
please cite Price et al., 2022, A&A 665 A159 (`ADS`_ | `arXiv`_).

.. _ADS: https://ui.adsabs.harvard.edu/abs/2022A%26A...665A.159P/abstract
.. _arXiv: https://arxiv.org/abs/2207.06442



License
###########
This project is Copyright (c) Sedona Price / MPE IR/Submm Group and licensed
under the terms of the BSD 3-Clause license. See the LICENSE.rst for more information.
