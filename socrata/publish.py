from socrata.resource import Collection
from socrata.revisions import Revisions
from socrata.http import headers, respond
import json
import requests

class Publish(Collection):
    def __init__(self, auth):
        super(Publish, self).__init__(auth)
        self.revisions = Revisions(auth)

    def new(self, body):
        path = 'https://{domain}/api/views'.format(
            domain = self.auth.domain
        )
        return respond(requests.post(
            path,
            headers = headers(),
            auth = self.auth.basic,
            verify = self.auth.verify,
            data = json.dumps(body)
        ))


