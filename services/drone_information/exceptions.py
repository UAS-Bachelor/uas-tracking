class RouteNotFoundException(Exception):

    def __init__(self, routeid):
        self.text = 'routeid {} does not exist'.format(routeid)
        super().__init__(self.text)