import sys
from utils import IxRestUtils, IxLoadUtils


class Connection:
    def __init__(self, server_ip, server_port, api_version):
        self.server_ip = server_ip
        self.server_port = server_port
        self.api_version = api_version
        self.connection = self.create_connection()
        self.session = self.create_session()

    def create_connection(self):
        IxLoadUtils.log("IxLoad: creating connection & session")
        return IxRestUtils.getConnection(self.server_ip, self.server_port, httpRedirect=False, version=self.api_version)

    def create_session(self):
        try:
            IxLoadUtils.deleteAllSessions(self.connection)
            return IxLoadUtils.startNewSession(self.connection)
        except AttributeError as ex:
            sys.exit("AttributeError while in ixia_connection.create_session()")

    def shutdown(self):
        IxLoadUtils.deleteSession(self.connection, self.session)
        IxLoadUtils.log("IxLoad: shutdown, bye!")
