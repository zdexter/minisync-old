import datetime

def rec_getattr(obj, attr):
    return reduce(getattr, attr.split('.'), obj)

class Serializer(object):
    """
    Mixin for SQLAlchemy mapper classes.
    Usage:
        Use this mixin, then set a property __public__ on your mapper class.
        __public__ is a list of properties on the mapper class instances or on related instances.
    """
    __public__ = None

    def __typeCheck(self, value):
        """
        Return a serializable form of value.
        TODO: Support configurable date formats
        """
        if isinstance(value, datetime.datetime):
            return value.isoformat()
        return value

    def to_serializable_dict(self):
        d = {}
        for attr in self.__public__:
            value = rec_getattr(self, attr)
            if value != None:
                if isinstance(value, list):
                    try:
                        d[attr] = [{k: self.__typeCheck(rec_getattr(x, k)) for k in x.__public__} for x in value]
                    except AttributeError:
                        d[attr] = value
                else:
                    d[attr] = self.__typeCheck(value)
        return d

