# macefash
personal FaceMash clone

<hr>

## Requirements
You need to have `python2.7` installed (`python3.4` should probably require slight adjustments to the code), as well as `Flask` and `SQLAlchemy`.

```console
sudo apt-get install python2.7 python-flask python-flask-sqlalchemy
```

This should be enough to get you covered. Additional tinkering might be necessary.

## How to deploy
Macefash can be run locally (on port 8080, by default) using the following command:
```console
python main.py
```

The port can be changed in the last line of the file:
```python
    app.run(host='0.0.0.0', port=8080, debug=True)
```
Using the `debug=True` flag is *not* recommended for production use.

## How to add data
The application creates a sample database with dummy entries. Additional entries can be added via command-line. A utility that simplifies the process will probably be built later on.
