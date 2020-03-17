from jahresdatenview import JahresdatenView
from jahresdatenprovider import JahresdatenProvider, JahresdatenCollection
import datehelper
#++++++++++++++++++++++++++++++++++++++++++++++++

class JahresdatenController:
    def __init__(self, dataProvider: JahresdatenProvider,
                 jahresdatenView: JahresdatenView):
        self._dataProvider = dataProvider
        self._view = jahresdatenView
        self._view.registerOnJahresdatenCallback(self._onGetJahresdaten)
        self._whg_id = None

    def startWork(self) -> None:
        pass

    def _onGetJahresdaten(self) -> None:
        l: List[JahresdatenCollection] = \
            self._dataProvider.getJahresdaten(self._whg_id, 2018, 2020)
        self._view.setValues(l)

    def wohnungSelected(self, whg_id: int) -> None:
        self.clear()
        self._whg_id = whg_id
        self._view.setButtonEnabled(True)

    def clear(self) -> None:
        self._whg_id = 0
        self._view.clear()
        self._view.setButtonEnabled(False)

def test():
    from tkinter import  Tk
    from tkinter import ttk
    import utils
    dp = JahresdatenProvider()
    dp.connect(utils.getUser())

    root = root = Tk()
    view = JahresdatenView(root)
    view.grid(column=0, row=0, sticky='nswe')
    ctrl = JahresdatenController(dp, view)
    ctrl.startWork()
    ctrl.wohnungSelected(1)

    root.mainloop()

if __name__ == '__main__':
    #messagebox.askokcancel("Title", "Message", icon='warning')
    test()