from business import DataProvider

class VermieterController:
    def __init__(self, dp:DataProvider):
        self._dataProvider:DataProvider = dp

    def createVermieter(self):
        print('VermieterController.createVermieter.')

    def editVermieter(self, vermieter_id:int):
        print('VermieterController.editVermieter. id=', vermieter_id)