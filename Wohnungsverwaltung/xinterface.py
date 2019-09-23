from typing import Dict, List, Text

class XInterface:
    def __init__(self, dic: Dict[str, any]):
        if dic:
            selfdict = self.__dict__
            for key in selfdict:
                if type(selfdict[key]) == int:
                    selfdict[key] = int(dic[key])
                elif type(selfdict[key]) == float:
                    selfdict[key] = float(dic[key])
                else:
                    selfdict[key] = dic[key]
            # for key in dic:
            #     self.__dict__[key] = dic[key]

    def setValue(self, attr_name: str, attr_value: any) -> None:
        self.__dict__[attr_name] = attr_value

    def getValue(self, attr_name) -> any:
        return self.__dict__[attr_name]

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class XInterfaceList:
    def __init__(self, klass: type, li: List[XInterface] = None):
        self._type = klass
        self._list = list()
        if li:
            self.setList(li)

    def setList(self, li: list) -> None:
        del self._list

        self._list = list()
        for item in li:
            if type(item) != dict:
                msg = ''.join((str(item), ' is not a dictionary'))
                raise TypeError(msg)
            dic = self._type(item)
            self._list.append(dic)

    def getList(self) -> List[XInterface]:
        return self._list

    def get(self, idx: int) -> XInterface:
        return self._list[idx]

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class XPerson(XInterface):
    def __init__(self, dic: dict = None):
        self.vorname = ''
        self.nachname = ''
        self.alter = 0
        XInterface.__init__(self, dic)

class Test:
    def __init__(self, s: str):
        self._s = s

    def get(self):
        return self._s

def testDictWrapper1():
    pd = {
        'vorname': 'Martin',
        'nachname': 'Kendel',
        'alter': '65'
    }

    xperson = XPerson(pd)
    xperson.setValue('nachname', 'Paulchen')
    print('xperson.nachname: ', xperson.nachname)
    print('xperson.getValue: ', xperson.getValue('nachname'))

    xpersonclass = globals()['XPerson']
    xperson2 = xpersonclass(pd)
    print(xperson2)

def testDictWrapperList():
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

    # w = XInterface(pd)
    plist = [
        pd,
        pd2
    ]

    l = XInterfaceList(XPerson, plist)
    print(l.getList()[0].vorname)


def main():
    testDictWrapper1()
    #testDictWrapperList()



if __name__ == '__main__':
    main()


