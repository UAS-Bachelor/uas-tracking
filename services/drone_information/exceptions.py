class RouteNotFoundException(Exception):

    def __init__(self, identifier):
        self.text = 'route could not be found by {}'.format(identifier)
        self.status_code = 404
        super().__init__(self.text, self.status_code)


class MissingKeyException(Exception):

    def __init__(self, key):
        self.text = 'missing key: {}'.format(key)
        self.status_code = 400
        super().__init__(self.text, self.status_code)
