from authomatic.providers import oauth2, oauth1

SETTINGS = {
    'auth': [('your_admin_username', 'your_admin_password')],
    'basePic': 'https://graph.facebook.com/%s/picture?width=%s&height=%s',
    'minVoteWait': 10.0, # time to wait between votes (in case of spam detection)
    'entriesOnPage': 30,
    'baseRating': 1700.0,
    'baseVolatility': 200.0,
    'defaultGender': False,
    'debug': False,
    'fb': {
        'class_': oauth2.Facebook,
        'consumer_key': '################',
        'consumer_secret': '################################',
        'scope': ['email', 'public_profile', 'user_friends']
        },
    'defaultTheme': (
        'Simplex',
        '//maxcdn.bootstrapcdn.com/bootswatch/3.3.4/simplex/bootstrap.min.css',
        'subtle_white_feathers.png'
        )
}
