class Hub(object):
    clients = set()

    @staticmethod
    def register(client):
        Hub.clients.add(client)

    @staticmethod
    def remove(client):
        if client in Hub.clients:
            Hub.clients.remove(client)

    @staticmethod
    def echo(sender, msg):
        for client in Hub.clients:
            if client != sender:
                client.send_text(msg)
