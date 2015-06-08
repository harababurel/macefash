# macefash
personal FaceMash clone

<hr>

## Inspiration
[![The Social Network - Facemash Scene](http://img.youtube.com/vi/b9jyEpCibYk/0.jpg)](https://www.youtube.com/watch?v=b9jyEpCibYk)

## Live version
The platform is currently running [here](http://macefash.ngrok.io/).

![vote page on desktop](https://raw.githubusercontent.com/harababurel/macefash/master/static/img/screens/vote_cyborg_no_ip.png)

![vote page mobile](https://raw.githubusercontent.com/harababurel/macefash/master/static/img/screens/iphone_6_6plus.png)

## Requirements
You need to have `python2.7` installed (`python3.4` should probably require slight adjustments to the code), as well as `Flask` (+ some plugins), `SQLAlchemy`, and [`authomatic`](http://peterhudec.github.io/authomatic/) (for the Facebook API).

```console
sudo apt-get install python2.7 python-flask python-flask-sqlalchemy
sudo pip install matplotlib numpy scipy
sudo pip install authomatic flask-debugtoolbar Flask-Cache
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
    app.run(host='0.0.0.0', port=8080, threaded=True, debug=SETTINGS['debug'])
```
Using the `debug=True` flag is **not** recommended for production use. The flag can be set in the `settings.py` config file.

You should now be able to access the platform on [localhost:8080](http://localhost:8080) :D.

## Resetting ratings
In case of any significant change to the rating system, all stats can be recomputed by simulating each real world vote.
There are two different rating functions implemented:
* The [TopCoder Component Development Rating](http://apps.topcoder.com/wiki/display/tc/Component+Development+Ratings) function - which is **probably bugged**. Ratings are considerably more sensible to losses than to wins, and they tend to converge in time.
* A more basic [Elo Rating](http://en.wikipedia.org/wiki/Elo_rating_system) function. So far, this looks promising.

The `computeRatings.py` module takes you through the process of recomputing all votes based on the **Elo Rating function**.
It can also generate a rating evolution graph for any person (`png` format, stored in the `static/graphs/` directory). Note that this is **experimental** and should only be used for checking whether or not the rating system behaves properly.

You should back up your database before attempting to reset ratings.
