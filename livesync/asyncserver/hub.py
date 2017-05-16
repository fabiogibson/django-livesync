class Hub(object):
    @staticmethod
    def clients():
        if not hasattr(Hub, '_clients'):
            Hub._clients = dict()
        return Hub._clients

    @staticmethod
    def register(client):
        Hub.clients()[client.id] = client

    @staticmethod
    def remove(client_id):
        if client_id in Hub.clients():
            del Hub.clients()[client_id]

    @staticmethod
    def echo(sender_id, msg):
        for client in Hub.clients().values():
            if client.id != sender_id:
                client.write_message(msg)
