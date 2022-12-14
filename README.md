# foae

A very quick and dirty tiny library for generating and exporting OpenAPI specs from Flask routes.

## Example

Given a Flask app:

```python
from flask import Flask

app = Flask(__name__)

[...]
```

And some routes defined elsewhere `/routes/sample.py`:

```python
@app.route('/')
def index():
    """Returns the index page"""
    pass

@app.route('/greet/<name>/<age>')
def greet(name: str, age: int):
    pass
```

We can attempt to export an OpenAPI spec:

```python
from foae import Foae
from routes import sample

sample_spec = Foae('example', '1.0.0')
sample_spec.parse(sample)
sample_spec.export_as('yaml') # Or json
```

Which gives us `openapi.yaml`:

```yaml
info:
  title: test
  version: 1.0.0
openapi: 3.1.0
paths:
  /:
    get:
      responses:
        200:
          description: Returns the index page
      tags:
        - index
  /greet/{name}/{age}:
    get:
      responses:
        200:
          description: Success
      tags:
        - greet
    parameters:
      - in: path
        name: name
        required: true
        schema:
          type: string
      - in: path
        name: age
        required: true
        schema:
          type: string
```
