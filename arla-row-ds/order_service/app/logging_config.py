"""
Struktureret logning. Logger hændelser i et ensartet format, så de kan
opsamles og analyseres i drift (et af de driftsmæssige krav i opgaven).
Hver vigtig hændelse — ordre modtaget, valideret, afvist, sendt til SAP —
logges eksplicit.
"""
import logging
import sys


def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        stream=sys.stdout,
    )
    return logging.getLogger("order-service")
