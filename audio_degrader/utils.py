import subprocess
import logging


def run(cmd):
    logging.debug(cmd)
    p = subprocess.Popen(cmd, shell=True,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    out, err = p.communicate()
    if p.returncode != 0:
        logging.error("Error running: " + cmd)
    return out, err
