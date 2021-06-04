#!/usr/bin/env python

import asyncio
from lsst.ts.pmd import PMDCsc

asyncio.run(PMDCsc.amain(index=True))
