"""
Base classes for endpoint and entitys
"""

import json
import collections
import sys
import os
from .exceptions import _ApiResponseError
from .exceptions import SdkEntityNotFound
from .exceptions import SdkEndpointNotFound
from .constants import PYTHON_3_0_0_HEXVERSION

__copyright__ = "Copyright 2017, Datera, Inc."


###############################################################################

def _is_stringtype(value):
    try:
        return isinstance(value, basestring)
    except NameError:
        return isinstance(value, str)


def get_init_func(klass):
    def paste_init(self, *args):
        super(klass, self).__init__(*args)
    return paste_init


def snake_to_camel(name):
    parts = name.split('_')
    return "".join(x.title() for x in parts)

###############################################################################


class Entity(collections.Mapping):
    """
    Entity object

    This is a mapping, so its attributes can be accessed just like a dict
    """
    _name = "base_entity"

    def __init__(self, context, data, name):
        """
        Parameters:
          context (dateraapi.context.ApiContext)
          data (dict)
        """
        self.context = context
        self._data = data

        # Set self._path:
        if 'path' in data:
            self._path = data['path']
            self._type = self.context.reader.get_entity(
                os.path.dirname(self._path))
            if not self._type:
                raise SdkEntityNotFound(
                    "/api endpoint did not contain entity: {} ".format(
                        os.path.dirname(self._path)))
        else:
            self._path = None
            self._type = {}
        if 'tenant' in data:
            self._tenant = data['tenant']
        else:
            self._tenant = None

        if name:
            self._name = name

        # In Python 2, dicts have has_key(); it was removed in Python 3.
        # So, do the same thing here:
        if sys.hexversion < PYTHON_3_0_0_HEXVERSION:
            self.has_key = self._has_key

    #
    # Implement dict-like interface

    def __len__(self):
        return len(self._data)

    def __getitem__(self, key):
        return self._data[key]

    def __iter__(self):
        return iter(self._data)

    def _has_key(self, key):
        """ True if this entity contains the given key, else False """
        return key in self

    def keys(self):
        return self._data.keys()

    def values(self):
        return self._data.values()

    def items(self):
        return self._data.items()

    ######

    def __str__(self):
        """ A human-readable representation of this entity """
        try:
            # Python 2
            return json.dumps(self._data, encoding='utf-8', indent=4)
        except TypeError:
            # Python 3
            return json.dumps(self._data, indent=4)

    def __repr__(self, **kwargs):
        version = self.context.connection._version
        t = snake_to_camel(self._type.get('name', ''))
        return "".join(("<", version, " ", t,
                        " ", str(self._path), " at 0x", str(id(self)), ">"))

    def __getattr__(self, attr):
        """ An attempt to give a functioning object back
        if no subendpoint of the requested name exists
        """
        if attr in self.__dict__:
            return self.__dict__[attr]
        else:
            if attr not in self.context.reader._ep_name_set:
                raise SdkEndpointNotFound(
                    "No {} Endpoint found for {}".format(
                        self.context.connection._version, attr))

            klass = type(snake_to_camel(attr), (GenericEndpoint,), {})
            klass.__init__ = get_init_func(klass)
            klass._name = attr
            return klass(self.context, self._path)

    ######

    # TODO(mss): Allow passing string, then determine the endpoint version
    def _set_subendpoint(self, klass):
        """ Create a sub-endpoint of the given endpoint type """
        assert(issubclass(klass, Endpoint))
        subendpoint = klass(self.context, self._path)
        subendpoint = self.context.prepare_endpoint(subendpoint)
        subendpoint_name = klass._name
        setattr(self, subendpoint_name, subendpoint)

    def reload(self, **params):
        """ Load a new instance of this entity from the API """
        if self._tenant:
            params = {'tenant': self._tenant}

        data = self.context.connection.read_entity(self._path, params)
        entity = self.__class__(self.context, data, self._name)
        entity = self.context.prepare_entity(entity)
        if self._tenant:
            entity._tenant = self._tenant
        return entity

    def set(self, **params):
        """ Send an API request to modify this entity """
        data = self.context.connection.update_entity(self._path, params)
        entity = self.__class__(self.context, data, self._name)
        entity = self.context.prepare_entity(entity)
        return entity

    def delete(self, **params):
        """ Send an API request to delete this entity """
        data = self.context.connection.delete_entity(self._path, data=params)
        entity = self.__class__(self.context, data, self._name)
        entity = self.context.prepare_entity(entity)

        # Call any on_delete hooks:
        entity = self.context.on_entity_delete(entity)
        return entity


###############################################################################


class Endpoint(object):
    """ REST API endpoint
        There should be a corresponding Entity Object created
        Eg, /network
    """

    _name = "base_endpoint"  # Subclass must initialize it
    _entity_cls = Entity  # Subclass must over-ride this

    def __init__(self, context, parent_path):
        """
        Parameters:
          context (dateraapi.context.ApiContext)
        """
        self.context = context
        self._path = None
        if (not parent_path and
                (self._name == "" or self._name == "base_endpoint")):
            self._path = ""  # root endpoint
        else:
            self._path = parent_path + '/' + self._name

    def __repr__(self):
        return "".join(("<", self.context.connection._version, ".",
                        snake_to_camel(self._name), "Ep", " ",
                        repr(self._path), ">"))

    def __getattr__(self, attr):
        """ An attempt to give a functioning object back
        if no subendpoint of the requested name exists
        """
        if attr in self.__dict__:
            return self.__dict__[attr]
        else:
            if attr not in self.context.reader._ep_name_set:
                raise SdkEndpointNotFound(
                    "No {} Endpoint found for {}".format(
                        self.context.connection._version, attr))

            klass = type(snake_to_camel(attr), (GenericEndpoint,), {})
            klass.__init__ = get_init_func(klass)
            klass._name = attr
            return klass(self.context, self._path)

    # TODO(mss): Allow passing string, then determine the endpoint version
    def _set_subendpoint(self, klass):
        """ Create a sub-endpoint of the given endpoint type """
        assert(issubclass(klass, Endpoint))
        subendpoint = klass(self.context, self._path)
        subendpoint = self.context.prepare_endpoint(subendpoint)
        subendpoint_name = klass._name
        setattr(self, subendpoint_name, subendpoint)

    def _get_list(self, _path, data):
        """ Returns a list of objects or strings, depending on the endpoint """
        if isinstance(data, list):
            return [self._prepare_data(value) for value in data]
        elif isinstance(data, dict):
            return [self._prepare_data(value)
                    for value in data.values()]
        else:
            raise ValueError("Unexpected response: " + repr(data))

    def _prepare_data(self, value):
        """
        If the data looks like a entity, create a Entity object from it,
        else just return it unchanged
        """
        if isinstance(value, dict):
            return self._new_contained_entity(value)
        else:
            return value

    def _new_contained_entity(self, data):
        """ Creates an Entity object """
        name = data.get('name')
        entity = self._entity_cls(self.context, data, name)
        entity = self.context.prepare_entity(entity)
        return entity

    def get(self, *args, **params):
        """
        Get a entity by its ID
        If no ID, return the whole collection
        """
        if len(args) == 0:
            # GET the whole collection
            path = self._path  # Eg. /storage_templates
            data = self.context.connection.read_endpoint(path, params)
            if isinstance(data, dict):
                for key in data:
                    data[key] = self._new_contained_entity(data[key])
                return data
            elif isinstance(data, list):
                return self._get_list(path, data)
            else:
                return data
        elif len(args) == 1:
            # GET a entity in the collection
            entity_id = args[0]
            # /storage_template/MyTemplate
            path = self._path + "/" + entity_id
            data = self.context.connection.read_entity(path, params=params)
            # This should return a single object in a dictionary form
            if isinstance(data, list):
                return self._get_list(path, data)
            return self._new_contained_entity(data)
        else:
            raise TypeError("Too many arguments for get()")


class GenericEndpoint(Endpoint):
    """ Catch-all endpoint for when one isn't defined by a type-spec
    but we still need to access it.  Allows most common operations.
    """

    def create(self, **params):
        """
        Create an entity in this collection

        Keyword arguments define the attributes of the created entity.
        """
        data = self.context.connection.create_entity(self._path, params)
        entity = self._new_contained_entity(data)

        # Call any on_create hooks:
        entity = self.context.on_entity_create(entity)
        return entity

    def set(self, **params):
        """Sets the endpoint with list passed"""
        data = self.context.connection.update_endpoint(self._path, params)
        return data

    def list(self, **params):
        """ Return all entities in this collection as a list """
        path = self._path
        try:
            data = self.context.connection.read_endpoint(path, params)
            return self._get_list(path, data)
        except _ApiResponseError as ex:
            if ex.message.startswith("No data at "):
                return []
            raise

    def get(self, **params):
        path = self._path
        data = self.context.connection.read_endpoint(path, params)
        return data
