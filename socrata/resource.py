import pprint
from socrata.http import noop, get
import requests

class Collection(object):
    def __init__(self, auth):
        self.auth = auth

    def subresources(self, klass, result):
        (ok, resources) = result
        if ok:
            return (ok, [klass(self.auth, res, self) for res in resources])
        return result

    def subresource(self, klass, result):
        (ok, res) = result
        if ok:
            return (ok, klass(self.auth, res, self))
        return result

class Resource(object):
    def __init__(self, auth, response, parent = None, *args, **kwargs):
        self.auth = auth
        self.on_response(response)
        self.parent = parent

    def on_response(self, response):
        self.attributes = response['resource']
        self.links = response['links']
        self.define_operations(self.links)

    def path(self, uri):
        return 'https://{domain}{uri}'.format(
            domain = self.auth.domain,
            uri = uri
        )

    def subresource(self, klass, result, **kwargs):
        (ok, res) = result
        if ok:
            return (ok, klass(self.auth, res, self, **kwargs))
        return result

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, pprint.pformat(self.attributes))

    def define_operations(self, links):
        for name, uri in links.items():
            setattr(self, name, self.dispatch(name, uri))
            setattr(self, '%s_uri' % name, uri)
        setattr(self, 'list_operations', lambda: list(links.keys()))

    # Yes this is kind of terrifying and bad and magic but i can't
    # think of a less obnoxious way to inject the uri
    def dispatch(self, name, uri):
        og_method_name = '_' + name
        if not hasattr(self, og_method_name):
            og_method = getattr(self, name, self.noop)
            setattr(self, og_method_name, og_method)

        old = getattr(self, og_method_name, self.noop)
        def f(*args, **kwargs):
            return old(uri, *args, **kwargs)
        return f

    def noop(self, uri, *args, **kwargs):
        raise NotImplementedError("%s is not implemented" % uri)

    def mutate(self, result):
        (ok, response) = result
        if ok:
            self.on_response(response)
            return (ok, self)
        return result

    # This is just the identity of this resource, so it's easy to abstract
    def show(self, uri):
        return self.mutate(get(
            self.path(uri),
            auth = self.auth
        ))
