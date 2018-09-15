from collections import defaultdict


class reify(object):
    """cached property"""

    def __init__(self, wrapped):
        self.wrapped = wrapped
        try:
            self.__doc__ = wrapped.__doc__
        except:
            pass

    def __get__(self, inst, objtype=None):
        if inst is None:
            return self
        val = self.wrapped(inst)
        setattr(inst, self.wrapped.__name__, val)
        return val


class NameStore:
    def __init__(self):
        self.c = defaultdict(int)
        self.value_map = {}  # (src_type, dst_type) => (name, i)

    def __contains__(self, value):
        return value in self.value_map

    def __setitem__(self, value, name):
        if value not in self.value_map:
            self.value_map[value] = self.get_name(value, name)
            self.c[name] += 1

    def __getitem__(self, value):
        return self.value_map[value]

    def get_name(self, value, name):
        try:
            return self[value]
        except KeyError:
            i = self.c[name]
            return self.new_name(name, i)

    def new_name(self, name, i):
        if i == 0:
            return name
        else:
            return "{}{:02d}".format(name, i)
