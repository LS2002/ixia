from utils import IxLoadUtils


class RXF:
    def __init__(self, connection):
        self.connection = connection.connection
        self.session = connection.session

    def get_url(self):
        return IxLoadUtils.getResourcesUrl(self.connection)

    def load_rxf(self, rxf_remote_path):
        IxLoadUtils.loadRepository(self.connection, self.session, rxf_remote_path)
        IxLoadUtils.log("RXF: loaded %s" % rxf_remote_path)

    def upload_rxf(self, rxf_path_local, rxf_path_server):
        IxLoadUtils.uploadFile(self.connection, self.get_url(), rxf_path_local, rxf_path_server)
        IxLoadUtils.log("RXF: uploaded to %s" % rxf_path_server)

    def save_rxf(self, rxf_remote_path):
        # save RXF
        IxLoadUtils.save(self.connection, self.session)
        IxLoadUtils.saveRxf(self.connection, self.session, rxf_remote_path, overWrite=True)
        IxLoadUtils.log("RXF: saved to %s" % rxf_remote_path)
