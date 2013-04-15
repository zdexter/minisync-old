from sqlalchemy.orm import class_mapper, ColumnProperty

class SyncObject(object):

    @staticmethod
    def __resolveAndSetAttribute(mapper_obj, attr_name, attr_val, id_col_name='id'):
        """
        Recursively resolve object-relational mappings until we get to a settable attribute.
        Notes:
            DO NOT use this method for now, as we allow association of arbitrary objects.
            We need proper validation and permissions hooks first.
        """
        if attr_name != id_col_name and attr_name in __attributeNames(mapper_obj.__class__):
            """
            Terminal attribute; resolves to a column on the current mapper.
            Don't update the ID column.
            """
            setattr(mapper_obj, attr_name, attr_val)
            return
        mapper_obj_or_iterable = getattr(mapper_obj, attr_name)
        """
        If mapper side is list, then for each key in attr_val, do decision proc:
            If key has ID, update
            Else, append
        """
        if isinstance(mapper_obj_or_iterable, list): # i-M relation
            indices_to_update = map(int, attr_val.keys())
            items_to_update_with_indices = list(enumerate(mapper_obj_or_iterable))
            items_to_update = filter(lambda x: hasattr(x[1], id_col_name) and x[0] in indices_to_update, items_to_update_with_indices)
            indices_to_update = [x[0] for x in items_to_update]

            items_to_associate = zip(attr_val.keys(), attr_val.values())
            items_to_associate = filter(lambda x: int(x[0]) not in indices_to_update, items_to_associate)
            for item in items_to_update:
                index_to_update, update_mapper_obj = item
                item_to_update = attr_val.get(str(item[0]))
                for k, v in item_to_update.iteritems(): # Recursively update all changed properties
                    SyncObject.__resolveAndSetAttribute(update_mapper_obj, k, v)
            for _, item_to_add in items_to_associate:
                # http://stackoverflow.com/questions/6843144/how-to-find-sqlalchemy-remote-side-objects-class-or-class-name-without-db-queri
                item_class = getattr(mapper_obj.__class__, attr_name).property.mapper.class_
                existing_id = item_to_add.get(id_col_name, None)
                if existing_id:
                    # TODO: Make sure user has permission to associate these objects
                    query = item_class.query
                    item_to_append = query.get(existing_id)
                else:
                    item_to_append = item_class()

                for k, v in item_to_add.iteritems():
                    SyncObject__resolveAndSetAttribute(item_to_append, k, v)
                mapper_obj_or_iterable.append(item_to_append)
        return mapper_obj
    
    @staticmethod
    def __attributeNames(mapper_class):
        return [prop.key.lstrip('_') for prop in class_mapper(mapper_class).iterate_properties
            if isinstance(prop, ColumnProperty)]
    
    @staticmethod
    def __unflatten(dictionary):
        resultDict = dict()
        for key, value in dictionary.iteritems():
            parts = key.split(".")
            d = resultDict
            for part in parts[:-1]:
                if part not in d:
                    d[part] = dict()
                d = d[part]
            d[parts[-1]] = value
        return resultDict

    @classmethod
    def syncObject(cls, mapper_class, mapper_obj_dict, delete=False, id_col_name='id', add_fn=db_add):
        """
        Create, update or delete the instance of mapper_class represented by mapper_obj_dict.
        Arguments:
            mapper_class - a metaclass
            mapper_obj_dict - a dict, dictionary whose keys are flattened representations of the rows or relations
                              we want to sync. Ex: `user.email.email` or `personal_statement`
                              Values can be scalars or lists. Lists are turned into sqlalchemy.orm.collection.InstrumentedList objects.
            [delete] - a boolean, whether (True) or not (False) to delete the object if it exists [False]
            [id_col_name] - an int, the name of the attr on mapper_class instances that should serve as an
                            existential check (TODO: Support multi-column primary keys)
            [add_fn] - a function, the function to use when adding a mapper object to the database
        Usage:
            Pass `id` to update (delete=False) or delete (delete=True). Leave out `id` to create.
        Return:
            - Create: ret_obj, the serialized created object, with an ID
            - Update: ret_obj, the serialized updated object, with changed fields only
            - Delete: None if deletion successful
        Raises:
            TODO
        """
        mapper_obj_dict = __unflatten(mapper_obj_dict)

        existing_id = mapper_obj_dict.get(id_col_name)
        mapper_obj = mapper_class()
        query_obj = getattr(mapper_obj, 'query')
        existing_record = query_obj.get(existing_id) if existing_id else None
        if existing_record: # Update or delete
            if delete:
                return db_remove(mapper_obj)
            for updated_field_name, updated_field_val in mapper_obj_dict.iteritems():
                cls.__resolveAndSetAttribute(existing_record, updated_field_name, updated_field_val)
            db.session.flush()
            db.session.commit()
            return existing_record
        else: # Create
            # TODO: Check for required fields
            return add_fn(mapper_obj)

