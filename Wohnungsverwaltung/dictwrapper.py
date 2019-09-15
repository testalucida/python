from typing import Dict, List, Text

class DictWrapper:
    def __init__(self, dic: Dict[str, str] = None):
        self._dict: Dict[str, str] = None
        if dic:
            self.setDict(dic)

    def setDict(self, dic: Dict[str, str]) -> None:
        for key in dic:
            self.__dict__[key] = dic[key]
        self._dict = dic

    def getDict(self) -> dict:
        return self._dict

    def setValue(self, attr_name, attr_value) -> None:
        self._dict[attr_name] = attr_value

    def getValue(self, attr_name) -> any:
        return self._dict[attr_name]

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class DictWrapperList:
    def __init__(self, klass: type, li: List[DictWrapper] = None):
        self._type = klass
        self._list: list = None
        if li:
            self.setList(li)

    def setList(self, li: list) -> None:
        if self._list:
            del self._list

        self._list = list()
        for item in li:
            if type(item) != dict:
                msg = ''.join((str(item), ' is not a dictionary'))
                raise TypeError(msg)
            dic = self._type(item)
            self._list.append(dic)

    def getList(self) -> List[DictWrapper]:
        return self._list

    def get(self, idx: int) -> DictWrapper:
        return self._list[idx]

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class XPerson(DictWrapper):
    def __init__(self, dic: dict = None):
        self.vorname: str = None
        self.nachname: str = None
        self.alter = None
        DictWrapper.__init__(self, dic)

class Test:
    def __init__(self, s: str):
        self._s = s

    def get(self):
        return self._s

def main():
    ttype = Test
    t = ttype("eine Instanz")
    print( t.get())

    pd = {
            'vorname': 'Martin',
            'nachname': 'Kendel',
            'alter': 'asbach'
        }

    pd2 = {
            'vorname': 'Pink',
            'nachname': 'Panter',
            'alter': '81'
        }

    #w = DictWrapper(pd)
    plist = [
        pd,
        pd2
    ]

    l = DictWrapperList(XPerson, plist)
    print(l.getList()[0].vorname)

if __name__ == '__main__':
    main()


