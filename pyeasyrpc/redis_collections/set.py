# -*- coding: utf-8 -*-
"""----------------------------------------------------------------------------
Author:
    Huang Quanyong (wo1fSea)
    quanyongh@foxmail.com
Date:
    2019/7/31
Description:
    set.py
----------------------------------------------------------------------------"""

from .redis_object import RedisObject


class Set(RedisObject):
    Redis_Type = "set"

    def __init__(self, key, packer=None, url=None):
        super(Set, self).__init__(key, packer, url)

    @property
    def data(self):
        return set(map(self.unpack, self._redis.smembers(self.key)))

    def add(self, element):
        """
        Add an element to a set.

        This has no effect if the element is already present.
        """
        b_element = self.pack(element)
        self._redis.sadd(self.key, b_element)

    def pop(self):
        """
        Remove and return an arbitrary set element.
        Raises KeyError if the set is empty.
        """
        if not len(self):
            raise KeyError()
        b_element = self._redis.spop(self.key)
        return self.unpack(b_element)

    def remove(self, element):
        """
        Remove an element from a set; it must be a member.

        If the element is not a member, raise a KeyError.
        """
        b_element = self.pack(element)
        if not self._redis.sismember(self.key, b_element):
            raise KeyError(b_element)
        self._redis.srem(self.key, b_element)

    def discard(self, element):
        """
        Remove an element from a set if it is a member.

        If the element is not a member, do nothing.
        """
        b_element = self.pack(element)
        self._redis.srem(self.key, b_element)

    def copy(self):
        return self.data

    def union(self, other):
        """
        Return the union of sets as a new set.

        (i.e. all elements that are in either set.)
        """
        if isinstance(other, Set):
            return set(map(self.unpack, self._redis.sunion(self.key, other.key)))
        else:
            return self.data.union(other)

    def update(self, other):
        """ Update a set with the union of itself and others. """
        if isinstance(other, Set):
            self._redis.sunionstore(self.key, self.key, other.key)
        else:
            for element in other:
                self.add(element)

    def difference(self, other):
        """
        Return the difference of two or more sets as a new set.

        (i.e. all elements that are in this set but not the others.)
        """
        if isinstance(other, Set):
            return set(map(self.unpack, self._redis.sdiff(self.key, other.key)))
        else:
            return self.data.difference(other)

    def difference_update(self, other):
        """ Remove all elements of another set from this set. """
        self._redis.srem(self.key, *map(self.pack, other))

    def intersection(self, other):
        """
        Return the intersection of two sets as a new set.

        (i.e. all elements that are in both sets.)
        """
        if isinstance(other, Set):
            return set(map(self.unpack, self._redis.sinter(self.key, other.key)))
        else:
            return self.data.intersection(other)

    def intersection_update(self, other):
        """ Update a set with the intersection of itself and another. """
        if isinstance(other, Set):
            self._redis.sinterstore(self.key, self.key, other.key)
        else:
            data = self.data.intersection(other)
            self.clear()
            if data:
                self._redis.sadd(self.key, *map(self.pack, data))

    def symmetric_difference(self, other):
        """
        Return the symmetric difference of two sets as a new set.

        (i.e. all elements that are in exactly one of the sets.)
        """
        return self.difference(other).union(other.difference(self.data))

    def symmetric_difference_update(self, other):
        """ Update a set with the symmetric difference of itself and another. """
        data = self.symmetric_difference(other)
        self.clear()
        if data:
            self._redis.sadd(self.key, *map(self.pack, data))

    def isdisjoint(self, other):
        """ Return True if two sets have a null intersection. """
        return not self.intersection(other)

    def issubset(self, other):
        """ Report whether another set contains this set. """
        if isinstance(other, Set):
            other = other.data

        return self.data.issubset(other)

    def issuperset(self, other):
        """ Report whether this set contains another set. """
        if isinstance(other, Set):
            other = other.data

        return self.data.issuperset(other)

    def __repr__(self):
        """ Return repr(self). """
        return repr(self.data)

    def __iter__(self):
        """ Implement iter(self). """
        return iter(self.data)

    def __len__(self):
        """ Return len(self). """
        return self._redis.scard(self.key)

    def __contains__(self, element):
        """ x.__contains__(y) <==> y in x. """
        b_element = self.pack(element)
        return self._redis.sismember(self.key, b_element)

    def __eq__(self, other):
        """ Return self==value. """
        if isinstance(other, Set):
            other = other.data
        return self.data == other

    def __ne__(self, other):
        """ Return self!=value. """
        if isinstance(other, Set):
            other = other.data
        return self.data != other

    def __ge__(self, other):
        """ Return self>=value. """
        if isinstance(other, Set):
            other = other.data
        return self.data >= other

    def __gt__(self, other):
        """ Return self>value. """
        if isinstance(other, Set):
            other = other.data
        return self.data > other

    def __le__(self, other):
        """ Return self<=value. """
        if isinstance(other, Set):
            other = other.data
        return self.data <= other

    def __lt__(self, other):
        """ Return self<value. """
        if isinstance(other, Set):
            other = other.data
        return self.data < other

    def __sub__(self, other):
        """ Return self-value. """
        return self.difference(other)

    def __rsub__(self, other):
        """ Return value-self. """
        if isinstance(other, Set):
            return other.difference(self)
        else:
            return other.difference(self.data)

    def __isub__(self, other):
        """ Return self-=value. """
        self.difference_update(other)
        return self

    def __and__(self, other):
        """ Return self&value. """
        return self.intersection(other)

    def __rand__(self, other):
        """ Return value&self. """
        return self.intersection(other)

    def __iand__(self, other):
        """ Return self&=value. """
        self.intersection_update(other)
        return self

    def __or__(self, other):
        """ Return self|value. """
        return self.union(other)

    def __ror__(self, other):
        """ Return value|self. """
        return self.union(other)

    def __ior__(self, other):
        """ Return self|=value. """
        self.update(other)
        return self

    def __xor__(self, other):
        """ Return self^value. """
        return self.symmetric_difference(other)

    def __rxor__(self, other):
        """ Return value^self. """
        return self.symmetric_difference(other)

    def __ixor__(self, other):
        """ Return self^=value. """
        self.symmetric_difference_update(other)
        return self
