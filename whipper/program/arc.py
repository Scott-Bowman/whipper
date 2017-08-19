from subprocess import Popen, PIPE

import logging
logger = logging.getLogger(__name__)

ARB = 'accuraterip-checksum'
FLAC = 'flac'


def accuraterip_checksum(f, track, tracks, wave=False, v2=False):
    v1 = '--accuraterip-v1'
    v2 = '--accuraterip-v2'

    track, tracks = str(track), str(tracks)

    if not wave:
        flac = Popen([FLAC, '-cds', f], stdout=PIPE)

        arc1 = Popen([ARB, v1, '/dev/stdin', track, tracks],
                    stdin=flac.stdout, stdout=PIPE, stderr=PIPE)
        arc2 = Popen([ARB, v1, '/dev/stdin', track, tracks],
                    stdin=flac.stdout, stdout=PIPE, stderr=PIPE)
    else:
        arc1 = Popen([ARB, v1, f, track, tracks],
                    stdout=PIPE, stderr=PIPE)

        arc2 = Popen([ARB, v2, f, track, tracks],
                    stdout=PIPE, stderr=PIPE)

    if not wave:
        flac.stdout.close()

    out1, err1 = arc1.communicate()
    out2, err2 = arc2.communicate()

    if not wave:
        flac.wait()
        flac_rc = flac.returncode

    arc_rc1 = arc1.returncode
    arc_rc2 = arc2.returncode

    if not wave and flac_rc != 0:
        logger.warning('ARC calculation failed: flac return code is non zero')
        return None

    if arc_rc1 != 0 or arc_rc2 != 0:
        logger.warning('ARC calculation failed: arc return code is non zero')
        return None

    out1 = out1.strip()
    out2 = out2.strip()

    try:
        outh1 = int('0x%s' % out1, base=16)
        outh2 = int('0x%s' % out2, base=16)
    except ValueError:
        logger.warning('ARC output is not usable')
        return None

    # return tuple
    return outh1, outh2
