#!/usr/bin/env python3
"""Contains miscellanous useful pieces of code."""

class MAAcumulator(object):
    """Store moving average data."""
    def __init__(self, period):
        self.period = period
        self.__data = []
        self.__window = []
    def add(self, data):
        """Add a new value and compute the MA if needed."""
        # TODO a better implementation would use cursors on a fixed-sized array
        self.__window.append(data)
        if len(self.__window) > self.period:
            self.__window.pop(0)
        if len(self.__window) == self.period:
            self.__data.append(self._mean_on_window())
    @property
    def data(self):
        """Return the MA data."""
        return self.__data
    def reset(self):
        """Clear all data, raw and MA."""
        self.__data.clear()
        self.__window.clear()
    def _mean_on_window(self):
        res = 0
        for i in self.__window:
            res += i
        res /= len(self.__window)
        return res
