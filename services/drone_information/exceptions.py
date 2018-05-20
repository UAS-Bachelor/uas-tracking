class RouteNotFoundException(Exception):

    def __init__(self, routeid):
        self.text = 'routeid {} does not exist'.format(routeid)
        super().__init__(self.text)


class MissingKeyException(Exception):

    def __init__(self, key):
        self.text = 'missing key: {}'.format(key)
        self.status_code = 400
        super().__init__(self.text, self.status_code)
