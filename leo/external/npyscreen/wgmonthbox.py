#@+leo-ver=5-thin
#@+node:ekr.20170428084208.43: * @file ../external/npyscreen/wgmonthbox.py
#!/usr/bin/env python

#@+others
#@+node:ekr.20170428084208.44: ** Declarations
from . import wgwidget as widget
import calendar
import datetime
import curses

#@+node:ekr.20170428084208.45: ** class DateEntryBase
class DateEntryBase(widget.Widget):
    #@+others
    #@+node:ekr.20170428084208.46: *3* __init__
    def __init__(self, screen, allowPastDate=True, allowTodaysDate=True, firstWeekDay=6,
                    use_datetime=False, allowClear=False, **keywords):
        super(DateEntryBase, self).__init__(screen, **keywords)
        self.allow_date_in_past = allowPastDate
        self.allow_todays_date = allowTodaysDate
        self.allow_clear = allowClear
        self.use_datetime = use_datetime
        self._max = datetime.date.max
        self._min = datetime.date.min
        self.firstWeekDay = firstWeekDay

    #@+node:ekr.20170428084208.47: *3* date_or_datetime
    def date_or_datetime(self):
        if self.use_datetime:
            return datetime.datetime
        else:
            return datetime.date

    #@+node:ekr.20170428084208.48: *3* _check_date
    def _check_date(self):
        if not self.value:
            return None
        if not self.allow_date_in_past:
            if self.value < self.date_or_datetime().today():
                if self.allow_todays_date:
                    self.value = self.date_or_datetime().today()
                else:
                    self.value = self.date_or_datetime().today() + datetime.timedelta(1)

    #@+node:ekr.20170428084208.49: *3* _check_today_validity
    def _check_today_validity(self, onErrorHigher=True):
        """If not allowed to select today's date, and today is selected, move either higher or lower
        depending on the value of onErrorHigher"""
        if not self.allow_date_in_past:
            onErrorHigher = True
        if self.allow_todays_date:
            return True
        else:
            if self.value == self.date_or_datetime().today():
                if onErrorHigher:
                    self.value += datetime.timedelta(1)
                else:
                    self.value -= datetime.timedelta(1)


    #@+node:ekr.20170428084208.50: *3* set_up_handlers
    def set_up_handlers(self):
        '''DataEntryBase.set_up_handlers.'''
        super(DateEntryBase, self).set_up_handlers()
        self.handlers.update({
            "D": self.h_day_less,
            "d": self.h_day_more,
            "W": self.h_week_less,
            "w": self.h_week_more,
            "M": self.h_month_less,
            "m": self.h_month_more,
            "Y": self.h_year_less,
            "y": self.h_year_more,
            "t": self.h_find_today,
            "q": self.h_clear,
            "c": self.h_clear,
        })
    #@+node:ekr.20170428084208.51: *3* _reduce_value_by_delta
    def _reduce_value_by_delta(self, delta):
        old_value = self.value
        try:
            self.value -= delta
        except Exception:
            self.value = old_value

    #@+node:ekr.20170428084208.52: *3* _increase_value_by_delta
    def _increase_value_by_delta(self, delta):
        old_value = self.value
        try:
            self.value += delta
        except Exception:
            self.value = old_value


    #@+node:ekr.20170428084208.53: *3* h_day_less
    def h_day_less(self, *args):
        self._reduce_value_by_delta(datetime.timedelta(1))
        self._check_date()
        self._check_today_validity(onErrorHigher=False)

    #@+node:ekr.20170428084208.54: *3* h_day_more
    def h_day_more(self, *args):
        self._increase_value_by_delta(datetime.timedelta(1))
        self._check_date()
        self._check_today_validity(onErrorHigher=True)

    #@+node:ekr.20170428084208.55: *3* h_week_less
    def h_week_less(self, *args):
        self._reduce_value_by_delta(datetime.timedelta(7))
        self._check_date()
        self._check_today_validity(onErrorHigher=False)

    #@+node:ekr.20170428084208.56: *3* h_week_more
    def h_week_more(self, *args):
        self._increase_value_by_delta(datetime.timedelta(7))
        self._check_date()
        self._check_today_validity(onErrorHigher=True)

    #@+node:ekr.20170428084208.57: *3* h_month_less
    def h_month_less(self, *args):
        self._reduce_value_by_delta(datetime.timedelta(28))
        self._check_date()
        self._check_today_validity(onErrorHigher=False)

    #@+node:ekr.20170428084208.58: *3* h_month_more
    def h_month_more(self, *args):
        self._increase_value_by_delta(datetime.timedelta(28))
        self._check_date()
        self._check_today_validity(onErrorHigher=True)

    #@+node:ekr.20170428084208.59: *3* h_year_less
    def h_year_less(self, *args):
        old_value = self.value
        try:
            if self.value.month == 2 and self.value.day == 29:
                self.value = self.value.replace(year=self.value.year - 1, day=self.value.day - 1)
            else:
                self.value = self.value.replace(year=self.value.year - 1)
            self._check_date()
            self._check_today_validity(onErrorHigher=False)
        except Exception:
            self.value = old_value

    #@+node:ekr.20170428084208.60: *3* h_year_more
    def h_year_more(self, *args):
        old_value = self.value
        try:
            if self.value.month == 2 and self.value.day == 29:
                self.value = self.value.replace(year=self.value.year + 1, day=self.value.day - 1)
            else:
                self.value = self.value.replace(year=self.value.year + 1)
            self._check_date()
            self._check_today_validity(onErrorHigher=True)
        except Exception:
            self.value = old_value

    #@+node:ekr.20170428084208.61: *3* h_find_today
    def h_find_today(self, *args):
        self.value = self.date_or_datetime().today()
        self._check_date()
        self._check_today_validity(onErrorHigher=True)

    #@+node:ekr.20170428084208.62: *3* .DateEntryBase.h_clear
    def h_clear(self, *args):
        if self.allow_clear:
            self.value = None
            self.editing = None

    #@-others
#@+node:ekr.20170428084208.63: ** class MonthBox
class MonthBox(DateEntryBase):
    DAY_FIELD_WIDTH = 4

    #@+others
    #@+node:ekr.20170428084208.64: *3* MonthBox.__init__
    def __init__(self, screen, **keywords):
        super(MonthBox, self).__init__(screen, **keywords)

    #@+node:ekr.20170428084208.65: *3* MonthBox.calculate_area_needed
    def calculate_area_needed(self):
        # Remember that although months only have 4-5 weeks, they can span 6 weeks.
        # Currently allowing 2 lines for headers, so 8 lines total
        return 10, self.__class__.DAY_FIELD_WIDTH * 7

    #@+node:ekr.20170428084208.66: *3* MonthBox.update
    def update(self, clear=True):
        calendar.setfirstweekday(self.firstWeekDay)
        if clear: self.clear()
        if self.hidden:
            self.clear()
            return False

        # Title line
        if not self.value:
            _title_line = "No Value Set"
        else:
            year = self.value.year
            month = self.value.month
            try:
                monthname = self.value.strftime('%B')
            except ValueError:
                monthname = "Month: %s" % self.value.month
            day = self.value.day

            _title_line = "%s, %s" % (monthname, year)

        if isinstance(_title_line, bytes):
            _title_line = _title_line.decode(self.encoding, 'replace')

        if self.do_colors():
            title_attribute = self.parent.theme_manager.findPair(self)
        else:
            title_attribute = curses.A_NORMAL

        self.add_line(self.rely, self.relx,
            _title_line,
            self.make_attributes_list(_title_line, title_attribute),
            self.width - 1
        )


        if self.value:
            # Print the days themselves
            try:
                cal_data = calendar.monthcalendar(year, month)
                do_cal_print = True
            except OverflowError:
                do_cal_print = False
                self.parent.curses_pad.addstr(self.rely + 1, self.relx, "Unable to display")
                self.parent.curses_pad.addstr(self.rely + 2, self.relx, "calendar for date.")
            if do_cal_print:
                # Print the day names
                # weekheader puts an extra space at the end of each name

                cal_header = calendar.weekheader(self.__class__.DAY_FIELD_WIDTH - 1)
                if isinstance(cal_header, bytes):
                    cal_header = cal_header.decode(self.encoding, 'replace')

                if self.do_colors():
                    cal_title_attribute = self.parent.theme_manager.findPair(self, 'LABEL')
                else:
                    cal_title_attribute = curses.A_NORMAL
                self.add_line(self.rely + 1, self.relx,
                    cal_header,
                    self.make_attributes_list(cal_header, cal_title_attribute),
                    self.width,
                    )

                print_line = self.rely + 2

                for calrow in cal_data:
                    print_column = self.relx

                    for thisday in calrow:
                        if thisday == 0:
                            pass
                        elif day == thisday:
                            if self.do_colors():
                                self.parent.curses_pad.addstr(print_line, print_column, str(thisday), curses.A_STANDOUT | self.parent.theme_manager.findPair(self, self.color))
                            else:
                                self.parent.curses_pad.addstr(print_line, print_column, str(thisday), curses.A_STANDOUT)
                        else:
                            if self.do_colors():
                                self.parent.curses_pad.addstr(print_line, print_column, str(thisday), self.parent.theme_manager.findPair(self, self.color))
                            else:
                                self.parent.curses_pad.addstr(print_line, print_column, str(thisday))
                        print_column += self.__class__.DAY_FIELD_WIDTH

                    print_line += 1

            # Print some help
            if self.allow_clear:
                key_help = "keys: dwmyDWMY t cq"
            else:
                key_help = "keys: dwmyDWMY t"

            if self.do_colors():
                self.parent.curses_pad.addstr(self.rely + 9, self.relx, key_help, self.parent.theme_manager.findPair(self, 'LABEL'))
            else:
                self.parent.curses_pad.addstr(self.rely + 9, self.relx, key_help)


    #@+node:ekr.20170428084208.67: *3* MonthBox.set_up_handlers
    def set_up_handlers(self):
        '''MonthBox.set_up_handlers.'''
        super(MonthBox, self).set_up_handlers()
        self.handlers.update({
            curses.KEY_LEFT: self.h_day_less,
            curses.KEY_RIGHT: self.h_day_more,
            curses.KEY_UP: self.h_week_less,
            curses.KEY_DOWN: self.h_week_more,
            curses.ascii.SP: self.h_exit_down,
            "^T": self.h_find_today,
        })

    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@-leo
