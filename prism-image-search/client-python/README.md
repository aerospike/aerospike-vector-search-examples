## Aerospike Proximus Vector Client Python

### Building using Python Virtual Environment
This is the recommended mode for building your Proximus applications using the python client.

```shell
# Virtual environment to isolate dependencies.
cd <your-application-directory>
python3 -m venv .venv
source .venv/bin/activate

# Install Proximus python client
cd <proximus-repo>/client-python/examples/prism-image-search
python3 setup.py develop

# Install application dependencies and run your application
cd <your-application-directory>
.
.
.
```

### Installing for all users

```shell
cd <proximus-repo>/client-python/examples/prism-image-search
sudo python3 setup.py develop
```

### Examples

See [examples](examples) for working sample code.
