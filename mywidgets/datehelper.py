
def convertIsoToEur(isostring: str) -> str:
    """
    converts an isodatestring into an eur datestring
    (2019-08-05 into 05.08.2019)
    :param isostring:
    :return:
    """
    iso = isostring.split('-')
    eur = ''.join((iso[2], '.', iso[1], '.', iso[0]))
    return eur