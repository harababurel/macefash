# macefash
personal FaceMash clone

<hr>

## Inspiration
[![The Social Network - Facemash Scene](http://img.youtube.com/vi/VSKoVsHs_Ko/0.jpg)](https://www.youtube.com/watch?v=VSKoVsHs_Ko)

## Live version
The platform is currently running [here](http://macefash.ngrok.io/).

![vote page on desktop](https://raw.githubusercontent.com/harababurel/macefash/master/static/img/screens/vote-cyborg-25sep2015.png)

([Older version](https://raw.githubusercontent.com/harababurel/macefash/master/static/img/screens/vote_cyborg_no_ip.png))

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
This will parse the local files (placed in `static/cns/`) and scrape all profile links from them. In addition to the profiles, the generator will also add a few themes for the website. Afterwards, each person's facebook ID is obtained and added to the database.

Profiles can be added to the local files in the following format:
* all files must be placed in `static/cns/`
* filenames must contain a number (`8-12`, depending on the grade) and a letter (`a-i`, depending on the class specialization); it is ok if some files are inexistent.
* each file contains the respective class' students, one on each line, as follows:
`GENDER_LETTER FULL_NAME FACEBOOK_PROFILE_URL` (note: `GENDER_LETTER` can be either `B` for male or `F` for female; I should change this in the future, so that English equivalents are used).
Check the existing files for clarification.

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

## Updating profile pictures

Since version 3.1, the platform caches profile pictures whenever they are missing from the server. This allows for greater control over what appears and what does NOT appear on macefash (there should also be some performance improvement). For example, if someone decides to close their account (or change their profile picture to [this](http://theimpersonals.com/wp-content/uploads/2013/01/lionel-richie-you-are.jpg)), the change does not take place immediately. Instead, you can update all (or some of the) profile pictures at the same time, and manage the unadequate ones manually.

This method ensures that you will not stumble upon any [white-head-on-grey-background](https://s-media-cache-ak0.pinimg.com/736x/0d/36/e7/0d36e7a476b06333d9fe9960572b66b9.jpg) picture while voting.

By default, pictures are saved when they are requested (make sure that the `static/pics/` directory exists, though). The following command updates all of them:
```console
python -c "from cacheSystem import *; buildEntireCache()"
```

The `cacheSystem.py` file also provides a method for updating specific pictures. Most of the time, there is no need for this.
