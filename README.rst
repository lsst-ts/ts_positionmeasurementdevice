############################
ts_positionmeasurementdevice
############################

PositionMeasurementDevice is a Commandable SAL Component for the `Vera C. Rubin Observatory <https://lsst.org>`_.
It controls devices that measure relative position displacement over a period of time.

Installation
============
pip/setuptools method

.. code::

    pip install -e .[dev]
    pytest --cov lsst.ts.positionmeasurementdevice -ra

EUPs method

.. code::

    setup -kr .
    scons

Requirements
------------
.. code::

    pre-commit install

This will run ``black`` as part of the ``git commit`` process.

Support
=======
Open issues on the JIRA project.

License
=======
This project is licensed under the `GPLv3 <https://www.gnu.org/licenses/gpl-3.0.en.html>`_.
