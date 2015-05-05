from macefash import db, models

option = None
while option is None or option not in range(1, 6):
    option = input(
            "model to query:\n" +
            "---> (1) Person\n" +
            "---> (2) Vote\n" +
            "---> (3) Message\n" +
            "---> (4) Theme\n" +
            "---> (5) UserSettings\n"
            )

what = [models.Person,
        models.Vote,
        models.Message,
        models.Theme,
        models.UserSettings
        ][option-1]

for x in db.session.query(what).all():
    print x, x.gender

db.session.close()
