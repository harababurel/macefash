# macefash
personal FaceMash clone

<hr>

## Inspiration
[![The Social Network - Facemash Scene](http://img.youtube.com/vi/b9jyEpCibYk/0.jpg)](https://www.youtube.com/watch?v=b9jyEpCibYk)

## Live version
The platform is currently running [here](http://macefash.ngrok.io/).

![vote page](https://raw.githubusercontent.com/harababurel/macefash/master/static/img/screens/vote_cyborg_no_ip.png)


## Requirements
You need to have `python2.7` installed (`python3.4` should probably require slight adjustments to the code), as well as `Flask` (+ some plugins), `SQLAlchemy`, and [`authomatic`](http://peterhudec.github.io/authomatic/) (for the Facebook API).

```console
sudo apt-get install python2.7 python-flask python-flask-sqlalchemy
sudo pip install authomatic
sudo pip install flask-debugtoolbar
```

This should be enough to get you covered. Additional tinkering might be necessary.

## How to deploy
First off, the database needs to be generated. In order to achieve this, run the following command:
```console
python databaseGenerator.py
```
This will parse the local files (placed in `static/cns/`) and scrape all profile links from them. In addition to the profiles, the generator will also add a few themes for the website.

*Note*: the script does **not** overwrite existing entries, so it can be safely executed in case of more profile links having been recently added to the local files. Only the new entries will suffer any changes. Keep in mind that some of them might need to be manually classified into genders (through the `genderHelp` interface).

Macefash can be run locally (on port `8080`, by default) using the following command:
```console
python main.py
```

The port can be changed in the last line of the file:
```python
    app.run(host='0.0.0.0', port=8080, threaded=True, debug=False)
```
Using the `debug=True` flag is **not** recommended for production use.

You should now be able to access the platform on [localhost:8080](http://localhost:8080) :D.
