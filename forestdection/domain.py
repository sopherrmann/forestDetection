from typing import List


class Timeseries:

    def __init__(self, dates: List[str] = None, sig0s: List[float] = None, name: str = None):
        self.name = name if name is not None else ''
        self.dates = dates if dates is not None else []
        self.sig0s = sig0s if sig0s is not None else []

    def push(self, date, sig0):
        self.dates.append(date)
        # TODO check if we ints are wanted?
        self.sig0s.append(int(sig0))

    def push_all(self, dates, sig0s):
        self.dates += dates
        self.sig0s += sig0s

    def update_name(self, name: str):
        self.name = name

    def get_zip(self):
        return zip(self.dates, self.sig0s)

    def get_attributes(self):
        return ['date', 'sig0']

    def get_sorted(self):
        sorted_ts = [(d, s) for d, s in sorted(self.get_zip())]
        return zip(*sorted_ts)

    def get_size(self):
        return len(self.dates)

    def __eq__(self, other):
        dates_check = self.dates == other.dates
        sig0_check = self.sig0s == other.sig0s
        return dates_check and sig0_check
