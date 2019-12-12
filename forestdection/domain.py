class Timeseries:

    def __init__(self, dates = None, sig0s = None):
        if dates is None:
            dates = []
        self.dates: list = dates
        if sig0s is None:
            sig0s = []
        self.sig0s: list = sig0s

    def push(self, date, sig0):
        self.dates.append(date)
        self.sig0s.append(sig0)

    def push_all(self, dates, sig0s):
        self.dates += dates
        self.sig0s += sig0s

    def get_zip(self):
        return list(zip(self.dates, self.sig0s))
