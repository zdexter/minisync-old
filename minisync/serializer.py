import datetime

def rec_getattr(obj, attr):
    try:
        ret_attr = reduce(getattr, attr.split('.'), obj)
    except AttributeError:
        ret_attr = None
    return ret_attr

class Serializer(object):
    __public__ = None
    
    @staticmethod
    def rec_serialize(attr):
        """
        Return:
            A value, if attr is a scalar
            A dictionary of key-value pairs, if attr is a db.Model instance
            A list, if attr is a list
            If a value is a nonterminal (list or db.Model instance), recurse.
        """
        d = {}
        if isinstance(attr, db.Model):
           return attr.to_serializable_dict()
        elif isinstance(attr, list):
            return [Serializer.rec_serialize(a) for a in attr]
        elif isinstance(attr, datetime.datetime):
            return attr.isoformat()
        return attr

    def to_serializable_dict(self, props=None):
        """
        Arguments:
            [props] - a list of strings, an optional list of property names to serialize.
                      If None, all string property names in self.__public__ will be serialized.
                      [None]
        """
        d = {}
        for attr_name in props or self.__public__:
            attr_to_serialize = rec_getattr(self, attr_name)
            d[attr_name] = Serializer.rec_serialize(attr_to_serialize)
        return d

