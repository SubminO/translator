class ServerError(Exception):
    pass


class ServerProtocolError(ServerError):
    pass


class ServerRegistrationError(ServerError):
    pass


class ServerClientRegistrationError(ServerRegistrationError):
    pass


# class