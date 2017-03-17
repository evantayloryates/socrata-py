import os
from socrata.authorization import Authorization
from socrata.publish import Publish

auth = Authorization(
  "localhost",
  os.environ['SOCRATA_LOCAL_USER'],
  os.environ['SOCRATA_LOCAL_PASS']
)

fourfour = "ij46-xpxe"


def create_rev():
    p = Publish(auth)
    (ok, r) = p.revisions.create(fourfour)
    assert ok
    return r

def create_input_schema():
    rev = create_rev()
    (ok, upload) = rev.create_upload({'filename': "foo.csv"})
    assert ok
    with open('test/fixtures/simple.csv', 'rb') as f:
        (ok, input_schema) = upload.csv(f)
        assert ok
        return input_schema

def create_output_schema():
    rev = create_rev()
    input_schema = create_input_schema()

    (ok, output_schema) = input_schema.transform({
        'output_columns': [
            {
                "field_name": "b",
                "display_name": "b, but as a number",
                "position": 0,
                "description": "b but with a bunch of errors",
                "transform": {
                    "transform_expr": "to_number(b)"
                }
            }
        ]}
    )
    assert ok
    return output_schema
