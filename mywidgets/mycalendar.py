from tkinter import *
from tkinter import ttk
import datetime
import calendar
import datehelper
from mywidgets import GetterSetter, ConvenianceMethods, ModifyTracer
#+++++++++++++++++++++++++++++++++++++++++++++++

class MonthCalendarProvider:
    def __init__(self, firstWeekDay: int = calendar.MONDAY, locale: str = 'de_DE'):
        self._cal = calendar.LocaleTextCalendar(firstWeekDay, locale)
        self.today = datetime.date.today()
        self._monthList = \
            ['Januar', 'Februar', 'März', 'April', 'Mai',
            'Juni', 'Juli', 'August', 'September',
            'Oktober', 'November', 'Dezember']
        self._dayList = ['Montag', 'Dienstag', 'Mittwoch',
                        'Donnerstag', 'Freitag', 'Samstag','Sonntag']
        self._currentMonthName = self._monthList[self.today.month-1]
        # TODO: get month list and day list in respect to given arg locale.
        # see calendar.formatmonthname(self, theyear, themonth, width, withyear=True)

    def getDayMatrix(self, year: int, month: int) -> list:
        #return a list of lists, one for each weak
        #cal = calendar.LocaleTextCalendar()
        return self._cal.monthdayscalendar(year, month)

    def getMonthNames(self) -> list:
        return self._monthList

    def getMonthName(self, month: int) -> str:
        return self._monthList[month-1]

    def getMonthIndex(self, month: str):
        #return the index of self._monthList, e.g. Januar => 0
        return self._monthList.index(month)

    def getMonthNumber(self, month: str):
        #returns the number of the given month,
        #e.g. Januar => 1
        return self.getMonthIndex(month) + 1

    def getDayNames(self) -> list:
        return self._dayList

    def getYears(self) -> list:
        return [2017, 2018, 2019, 2020, 2021, 2022]

    def getCurrentYear(self) -> int:
        return self.today.year

    def getCurrentMonth(self) -> int:
        #return the number of current month,
        #e.g. Januar => 1
        return self.today.month

    def getCurrentDay(self) -> int:
        return self.today.day

    def isToday(self, y: int, m: str, day: int) -> bool:
        return (y == self.today.year and  \
                m == self._currentMonthName and \
                day == self.today.day)

#+++++++++++++++++++++++++++++++++++++++++++++++

class CalendarDialog(Toplevel):
    def __init__(self, parent, initDate: datetime.date = None):
        Toplevel.__init__(self, parent)
        self.title("Kalender")
        self.bind('<Key>', self._onKeyHit) #handle escape key
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self._cal = MonthCalendarProvider()
        self._selectedYear = None #textvariable for year-combobox
        self._selectedMonth = None #textvariable für month-combobox
        self._monthCombo = None
        self._yearCombo = None
        self._daysframe = None #frame containing the day label matrix
        self._selectedDayLabel = None #the day user has clicked
        self._selectedDate = None #user's selection. None if user cancels the dialog
        self._selectedDayLabelBackground = None
        self._callback = None

        self._createGui()

        selectDay = True
        if not initDate:
            initDate = self._cal.today
            selectDay = False

        self.setDate(initDate, selectDay)

    def _createGui(self):
        framerow = 0
        #create a frame containing month and year
        myframe = ttk.Frame(self)
        myframe.grid(column=0, row=framerow)

        #create a combobox with month names
        self._selectedMonth = StringVar()
        mcombo = ttk.Combobox(myframe, state='readonly',
                              textvariable=self._selectedMonth,
                              values=self._cal.getMonthNames(),
                              width=10)
        mcombo.bind('<<ComboboxSelected>>', self._monthOrYearModified)
        mcombo.grid(column=0, row=0, sticky='nswe')
        self._monthCombo = mcombo

        #create a combobox with some years
        self._selectedYear = IntVar()
        ycombo = ttk.Combobox(myframe, state='readonly',
                              textvariable=self._selectedYear,
                              values=self._cal.getYears(),
                              width = 6)
        ycombo.grid(column=1, row=0, sticky='nswe')
        ycombo.bind('<<ComboboxSelected>>', self._monthOrYearModified)
        self._yearCombo =ycombo


        #create a frame containing day names
        framerow += 1
        dframe = ttk.Frame(self)
        dframe.grid(column=0, row=framerow, sticky='nswe')
        #create 7 Labels showing weekday names
        days = self._cal.getDayNames()
        for c in range(7):
            lbl = ttk.Label(dframe, width=3, background='lightgray',
                            text=str(days[c][:2]), anchor='center')
            lbl.grid(column=c, row=0, sticky='nswe', padx=1, pady=1)

        #create a frame containing matrix of days
        framerow += 1
        daysframe = ttk.Frame(self)
        daysframe.grid(column=0, row=framerow, sticky='nswe')
        self._daysframe = daysframe
        #self._createDaysMatrix(daysframe)

        #create a frame containing OK and Cancel buttons
        framerow += 1
        bframe = ttk.Frame(self)
        bframe.grid(column=0, row = framerow, sticky='nswe')
        okBtn = ttk.Button(bframe, text='OK', command=self.onOk)
        okBtn.grid(column=0, row=0, sticky='nswe')

        cancelBtn = ttk.Button(bframe, text='Cancel', command=self.onCancel)
        cancelBtn.grid(column=1, row=0, sticky='nswe')


    def _createDaysMatrix(self, parent: ttk.Frame,
                          year: int, month: int, day: int = None,
                          selectDay: bool = True) -> None:
        if day is None:
            day = -1

        #first destroy prior Labels
        self._clearDaysFrame()

        # create a label for each day which will result
        # in 7 labels a row.
        # Maximum rows is 6 so we will create max 42 labels.
        today = self._cal.today
        isCurrentMonth = \
            True if today.year == year and today.month == month else False
        matrix = self._cal.getDayMatrix(year, month)
        for row in range(len(matrix)):
            week = matrix[row]
            for col in range(7):
                d = week[col]
                text = ' ' if d == 0 else str(d)
                bg = 'yellow' if isCurrentMonth and d == today.day else 'white'

                relief = 'raised' if isCurrentMonth and d == today.day else 'flat'
                lbl = ttk.Label(parent, width=3, background=bg,
                                text=text, anchor='center', relief = relief)

                if d == day and selectDay:
                   self._setDaySelected(lbl)

                lbl.bind("<Button-1>", self._dayClicked)
                lbl.grid(column=col, row=row, sticky='nswe', padx=1, pady=1)

    def _clearDaysFrame(self):
        for child in self._daysframe.winfo_children():
            child.destroy()
        self._selectedDate = None
        self._selectedDayLabel = None
        self._selectedDayLabelBackground = None

    def _monthOrYearModified(self, evt):
        today = self._cal.today
        year = self._selectedYear.get()
        month = self._cal.getMonthNumber(self._selectedMonth.get())
        day = today.day if year == today.year and month == today.month else None

        self._createDaysMatrix(self._daysframe, year, month, day, False)
        self._selectedDate = None

    def _dayClicked(self, evt):
        text = evt.widget['text']
        if text == ' ':
            self._selectedDate = None
            return
        self._setDaySelected(evt.widget)

    def _setDaySelected(self, label: ttk.Label) -> None:
        # reset prior selection:
        if self._selectedDayLabel is not None:
            self._selectedDayLabel['background'] = self._selectedDayLabelBackground

        #remember label's state prior to markup
        self._selectedDayLabel = label
        self._selectedDayLabelBackground = label['background']

        #markup
        label['background'] = 'lightblue'

        self._selectedDate = \
            datetime.date(self._selectedYear.get(),
                          self._cal.getMonthNumber(self._selectedMonth.get()),
                          int(label['text']))

    def setSelectedCallback(self, callback):
        #sets a function which is to be called when user hits OK
        self._callback = callback

    def setCalendarCallback(self, callback):
        #sets a function which will be called when
        #  - a date is selected and OK is hit
        #  - Calendar instance is destroyed
        self._calendarCallback = callback
        #TODO: call this method on OK and destroy

    def setDate(self, date: datetime.date, selectDay: bool = True) -> None:
        #shows the month of the given date and marks the day.
        self._monthCombo.set(self._cal.getMonthName(date.month))
        self._yearCombo.set(date.year)
        self._createDaysMatrix(self._daysframe, date.year, date.month, date.day, selectDay)

    def setPosition(self, x: int, y: int) -> None:
        self.geometry("+%d+%d" % (x , y ))

    def onOk(self):
        if self._selectedDate is None:
            return

        if self._callback:
            self._callback(self._selectedDate)
        self.destroy()

    def onCancel(self):
        self.destroy()

    def _onKeyHit(self, evt):
        if evt.keycode == 9: #escape
            self.onCancel()

#+++++++++++++++++++++++++++++++++++++++++++++++

class DateEntry(ttk.Entry, GetterSetter, ConvenianceMethods, ModifyTracer):
    #Widget to display a date in german format dd.mm.yyyy
    #It's a composed widget consisting of an ttk.Entry field and
    #a Calendar Dialog that opens when user left clicks in the entry field.
    #When the user left clicks a date the dialog closes and the clicked value
    #will be provided into the entry field.
    def __init__(self, parent):
        ttk.Entry.__init__(self, parent,  validate="key")
        ConvenianceMethods.__init__(self)
        ModifyTracer.__init__(self)
        vcmd = (self.register(self.onValidate), '%P', '%S')
        self['validatecommand'] = vcmd
        self.bind("<Button-1>", self.openCalendarDialog)
        self.bind("<Key>", self._onKeyHit)
        self.bind("<FocusOut>", self._onFocusOut)
        self.bind("<FocusIn>", self._onFocusIn)
        self._text = StringVar()
        self['textvariable'] = self._text
        self._text.trace('w', self._onTextChange)
        self._useCalendar = True
        self._date = None
        self._dlg = None
        #validation:
        self._templateList = \
            [['n', '.', 'n', '.', 'n', 'n', 'n', 'n'],
             ['n', 'n', '.', 'n', '.', 'n', 'n', 'n', 'n'],
             ['n', '.', 'n', 'n', '.', 'n', 'n', 'n', 'n'],
             ['n', 'n', '.', 'n', 'n', '.', 'n', 'n', 'n', 'n']]

    @classmethod
    def fromIsoDatestring(cls, parent, datestring: str):
        return(cls(parent, datehelper.convertIsoToEur(datestring)))

    # @staticmethod
    # def convertIsoToEur(isostring: str) -> str:
    #     """
    #     converts an isodatestring into an eur datestring
    #     (2019-08-05 into 05.08.2019)
    #     :param isostring:
    #     :return:
    #     """
    #     iso = isostring.split('-')
    #     eur = ''.join(iso[2], '.', iso[1], '.', iso[0])
    #     return eur


    def _onKeyHit(self, evt):
        if evt.state == 20 and evt.keycode == 65: #Ctrl+space
            self.openCalendarDialog(None)

    def _onFocusOut(self, evt):
        text = self._text.get()
        if len(text) == 0: return
        #final check: try to create a datetime.date out of the given entry
        parts = text.split('.')
        if len(parts) < 3:
            self._onWrongFormat()
            return
        try:
            dt = datetime.date(int(parts[2]), int(parts[1]), int(parts[0]))
        except:
            self._onWrongFormat()

    def _onFocusIn(self, evt):
        self['style'] = 'TEntry'

    def _onWrongFormat(self):
        st = ttk.Style()
        st.configure('My.TEntry', fieldbackground='red')
        #print("Wrong format: ", self._text.get())
        self['style'] = 'My.TEntry'

    def onValidate(self, P, S):
        if (S >= '0' and S <= '9') or S == '.':
            for n in range(len(self._templateList)):
                ok = self._matches(P, self._templateList[n])
                if ok: return True

        return False

    def _matches(self, preview: str, t: list) -> bool:
        #print('matches() invoked with: preview=', preview, 't=', t)
        l = len(preview)
        if l > len(t): return False

        for i in range(l):
            if t[i] == '.':
                if preview[i] != '.':
                    return False
            else:  # t = 'n'
                if preview[i] == '.':
                    return False
        return True

    def setUseCalendar(self, use: bool) -> None:
        self._useCalendar = use

    def openCalendarDialog(self, event):
        if self._useCalendar:
            root = self._getRoot()
            self._dlg = CalendarDialog(root, self._date)
            #dialog "always on top":
            self._dlg.attributes('-topmost', 'true')
            #self._dlg.wm_overrideredirect(True)
            rootx = root.winfo_x()
            rooty = root.winfo_y()
            x = self.winfo_x()
            y = self.winfo_y()
            self._dlg.setPosition(rootx + x, rooty + y + 30)
            #self.wait_window(dlg)
            self._dlg.setSelectedCallback(self._dateSelected)
            # when dialog is visible we can set grab:
            self._dlg.bind('<Visibility>', self.onVisible)

    def onVisible(self, evt):
        #when dialog is open, we don't want any input into parent frame:
        self._dlg.grab_set()

    def _dateSelected(self, selectedDate: datetime.date) -> None:
        self._date = selectedDate
        datestring = selectedDate.strftime("%d.%m.%Y")
        self._text.set(datestring)

        self._dlg = None

    def _onTextChange(self, *args):
        pass

    def setDate(self, datestring: str) -> None:
        # datestring: format d.m.yyyy required or empty string
        if datestring:
            sep = '.' if datestring.find('.') > 0 else '-'
            parts = datestring.split(sep)
            if len(parts) < 3:
                raise ValueError("The given date string doesn't meet the "
                                 "needed format (d)d.(m)m.yyyy")
            #if sep == '.':
            n = (2, 1, 0) if sep == '.' else (0, 1, 2)

            try:
                dt = datetime.date(int(parts[n[0]]), int(parts[n[1]]), int(parts[n[2]]))
            except:
                raise ValueError("The given date string doesn't meet the "
                                 "needed format (d)d.(m)m.yyyy")
        self.clear()
        self.insert(0, datestring)

    def getValue(self) -> any:
        return self.get()

    def setValue(self, val: str) -> None:
        if val:
            self.setDate(val)

    def clear(self):
        self.delete(0, 'end')

    def _getRoot(self):
        master = mastermem = self.master
        while master:
            mastermem = master
            master = master.master
        return mastermem
