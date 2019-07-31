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
        raise NotImplementedError()

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
        raise NotImplementedError()

    def difference_update(self, other):
        """ Remove all elements of another set from this set. """
        raise NotImplementedError()

    def intersection(self, *args, **kwargs):
        """
        Return the intersection of two sets as a new set.

        (i.e. all elements that are in both sets.)
        """
        raise NotImplementedError()

    def intersection_update(self, *args, **kwargs):
        """ Update a set with the intersection of itself and another. """
        raise NotImplementedError()

    def isdisjoint(self, *args, **kwargs):
        """ Return True if two sets have a null intersection. """
        raise NotImplementedError()

    def issubset(self, *args, **kwargs):
        """ Report whether another set contains this set. """
        raise NotImplementedError()

    def issuperset(self, *args, **kwargs):
        """ Report whether this set contains another set. """
        raise NotImplementedError()

    def symmetric_difference(self, *args, **kwargs):
        """
        Return the symmetric difference of two sets as a new set.

        (i.e. all elements that are in exactly one of the sets.)
        """
        raise NotImplementedError()

    def symmetric_difference_update(self, *args, **kwargs):
        """ Update a set with the symmetric difference of itself and another. """
        raise NotImplementedError()

    def union(self, *args, **kwargs):
        """
        Return the union of sets as a new set.

        (i.e. all elements that are in either set.)
        """
        raise NotImplementedError()

    def __repr__(self, *args, **kwargs):
        """ Return repr(self). """
        raise NotImplementedError()

    def __iter__(self, *args, **kwargs):
        """ Implement iter(self). """
        raise NotImplementedError()

    def __len__(self, *args, **kwargs):
        """ Return len(self). """
        raise NotImplementedError()

    def __contains__(self, y):
        """ x.__contains__(y) <==> y in x. """
        raise NotImplementedError()

    def __eq__(self, *args, **kwargs):
        """ Return self==value. """
        raise NotImplementedError()

    def __ne__(self, *args, **kwargs):
        """ Return self!=value. """
        raise NotImplementedError()

    def __ge__(self, *args, **kwargs):
        """ Return self>=value. """
        raise NotImplementedError()

    def __gt__(self, *args, **kwargs):
        """ Return self>value. """
        raise NotImplementedError()

    def __le__(self, *args, **kwargs):
        """ Return self<=value. """
        raise NotImplementedError()

    def __lt__(self, *args, **kwargs):
        """ Return self<value. """
        raise NotImplementedError()

    def __sub__(self, *args, **kwargs):
        """ Return self-value. """
        raise NotImplementedError()

    def __rsub__(self, *args, **kwargs):
        """ Return value-self. """
        raise NotImplementedError()

    def __isub__(self, *args, **kwargs):
        """ Return self-=value. """
        raise NotImplementedError()

    def __and__(self, *args, **kwargs):
        """ Return self&value. """
        raise NotImplementedError()

    def __rand__(self, *args, **kwargs):
        """ Return value&self. """
        raise NotImplementedError()

    def __iand__(self, *args, **kwargs):
        """ Return self&=value. """
        raise NotImplementedError()

    def __or__(self, *args, **kwargs):
        """ Return self|value. """
        raise NotImplementedError()

    def __ror__(self, *args, **kwargs):
        """ Return value|self. """
        raise NotImplementedError()

    def __ior__(self, *args, **kwargs):
        """ Return self|=value. """
        raise NotImplementedError()

    def __xor__(self, *args, **kwargs):
        """ Return self^value. """
        raise NotImplementedError()

    def __rxor__(self, *args, **kwargs):
        """ Return value^self. """
        raise NotImplementedError()

    def __ixor__(self, *args, **kwargs):
        """ Return self^=value. """
        raise NotImplementedError()
