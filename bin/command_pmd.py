import asyncio
from lsst.ts import salobj

asyncio.run(salobj.CscCommander.amain(name="PMD", index=True))
