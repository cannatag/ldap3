import collections


class CaseInsensitiveDict(collections.MutableMapping):
    if bytes == str:  # python2
        case_insensitive_types = (str, unicode)
    else:  # python3
        case_insensitive_types = (str,)

    def __init__(self, other=None, **kwargs):
        self._store = dict()
        if other or kwargs:
            if other is None:
                other = dict()
            self.update(other, **kwargs)

    def _getkey(self, key):
        if isinstance(key, CaseInsensitiveDict.case_insensitive_types):
            for stored_key in self._store:
                if isinstance(stored_key, CaseInsensitiveDict.case_insensitive_types):
                    if key.lower() == stored_key.lower():
                        key = stored_key
                        break
        return key

    def __delitem__(self, key):
        del self._store[self._getkey(key)]

    def __setitem__(self, key, item):
        self._store[self._getkey(key)] = item

    def __getitem__(self, key):
        return self._store[self._getkey(key)]

    def __iter__(self):
        return self._store.__iter__()

    def __len__(self):
        return len(self._store)

    def __repr__(self):
        return repr(self._store)

    def __str__(self):
        return str(self._store)

    def __eq__(self, other):
        if not isinstance(other, collections.Mapping):
            return NotImplemented

        if isinstance(other, CaseInsensitiveDict):
            if isinstance(self.items(), list):  # python 2
                if len(self.items()) != len(other.items()):
                    return False
                else:
                    for key, value in self.items():
                        if not (key in other and other[key] == value):
                            return False
                    return True
            else:
                return self.items() == other.items()

        return self == CaseInsensitiveDict(other)

    def copy(self):
        return CaseInsensitiveDict(self._store)
