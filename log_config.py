# ========================================
# log config
# ========================================

import logging

# this variable have to be exported in order to get logs
logger = logging.getLogger("myapp")
logger.setLevel(logging.INFO)

# Stream Handler
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)  # show DEBUG+ on console
fmt = logging.Formatter("%(levelname)s %(name)s: %(message)s")
ch.setFormatter(fmt)
logger.addHandler(ch)

logger.propagate = False
