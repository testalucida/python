
def convertIsoToEur(isostring: str) -> str:
    """
    converts an isodatestring into an eur datestring
    (2019-08-05 into 05.08.2019)
    :param isostring:
    :return: a converted datestring
    """
    if not isostring:
        return ''

    iso = isostring.split('-')
    eur = ''.join((iso[2], '.', iso[1], '.', iso[0]))
    return eur

def convertEurToIso(eurstring: str) -> str:
    """
    converts an eurdatestring int an iso datestring
    ('29.08.2019' into '2019-08-29')
    :param eurstring:
    :return: a converted datestring
    """
    if not eurstring:
        return ''

    eur = eurstring.split('.')
    iso = ''.join((eur[2], '-', eur[1], '-', eur[0]))
    return iso
