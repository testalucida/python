from typing import List
from PySide2.QtCore import QObject

import datehelper
from v2.icc.icclogic import IccLogic


class IccController( QObject ):
    def __init__( self ):
        dic = datehelper.getCurrentYearAndMonth()
        self._year = dic["year"]
        self._month = dic["month"] - 1
        self._icclogic = IccLogic()

    def getYearAndMonthToStartWith( self ):
        """
        Liefert Jahr und Monat, das bei Anwendungsstart zu verwenden ist
        :return:
        """
        return self._year, self._month

    def getYearToStartWith( self ):
        """
        Liefert das Jahr das bei Anwendungsstart zu verwenden ist
        :return:
        """
        return self._year

    def getJahre( self ) -> List[int]:
        return self._icclogic.getJahre()