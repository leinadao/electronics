class NoClearControl (Exception):
    '''
        An exception for trying to
        use an uncontrolled clear.
    '''

    def __init__ (self, message = None):
        '''
            Use a standard message if
            not given one.
        '''
        if not message:
            message = 'The clear pin is not being controlled.'
        super ().__init__ (self, message)
