import urlparse
import httplib

def solveRedirect(url, depth=0):
    """
    Facebook API provides a URL for acquiring profile pictures.
    That URL contains a person's username, which is not wanted.
    However, the URL redirects to an encrypted link, which can then be used.
    This function gets the encrypted address
    """

    if depth > 2:
        raise Exception("redirected %i times, giving up." % depth)
    o = urlparse.urlparse(url, allow_fragments=True)
    conn = httplib.HTTPConnection(o.netloc)
    path = o.path
    if o.query:
        path += '?' + o.query

    conn.request("HEAD", path)
    res = conn.getresponse()
    headers = dict(res.getheaders())

    if headers.has_key('location') and headers['location'] != url:
        return solveRedirect(headers['location'], depth+1)
    return url
