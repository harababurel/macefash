from authomatic.providers import oauth2, oauth1

SETTINGS = {
    'auth': [('cauciuc', 'dezosat')],
    'basePic': 'https://graph.facebook.com/%s/picture?width=%s&height=%s',
    'minVoteWait': 10.0,
    'entriesOnPage': 30,
    'baseRating': 1200.0,
    'baseVolatility': 385.0,
    'fb': {
        'class_': oauth2.Facebook,
        'consumer_key': '1636893603200226',
        'consumer_secret': '650a122a687e8e9baa444138bd31a692',
        'scope': ['email', 'public_profile', 'user_friends']
        },
    'defaultTheme': (
        'Simplex',
        '//maxcdn.bootstrapcdn.com/bootswatch/3.3.4/simplex/bootstrap.min.css',
        'subtle_white_feathers.png'
        )
}
