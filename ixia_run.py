from utils import IxLoadUtils


class Run:
    def __init__(self, connection, timeout):
        self.connection = connection.connection
        self.session = connection.session
        self.timeout = timeout

    def start_test(self):
        IxLoadUtils.log("Run: test starting...")
        IxLoadUtils.runTest(self.connection, self.session)
        test_error = IxLoadUtils.getTestRunError(self.connection, self.session)
        if test_error:
            IxLoadUtils.log("Run: exited with error - %s" % test_error)
        IxLoadUtils.log("Run: test started")

    def wait_test(self):
        IxLoadUtils.waitForTestToReachUnconfiguredState(self.connection, self.session, self.timeout)
        IxLoadUtils.log("Run: wait test ended successfully")

    def stop_test(self):
        IxLoadUtils.log("Run: stopping...")
        IxLoadUtils.releaseConfiguration(self.connection, self.session)
        IxLoadUtils.log("Run: test stopped")
