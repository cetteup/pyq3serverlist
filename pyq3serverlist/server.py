class Server:
    ip: str
    port: int

    def __init__(self, ip: str, port: int):
        self.ip = ip
        self.port = port

    def __repr__(self):
        return f'{self.ip}:{self.port}'

    def __iter__(self):
        yield 'ip', self.ip
        yield 'port', self.port
