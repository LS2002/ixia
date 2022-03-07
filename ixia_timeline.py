from utils import IxLoadUtils


class Timeline:
    def __init__(self, connection):
        self.connection = connection.connection
        self.session = connection.session

    def get_timeline_list_url(self):
        return "%s/ixload/test/activeTest/timelineList" % self.session

    def get_timeline_item_url(self, timeline_id):
        return "%s/%s" % (self.get_timeline_list_url(), timeline_id)

    def set_time(self, run_time_in_hours):
        timeline_list_url = self.get_timeline_list_url()
        timelines = IxLoadUtils.performGenericGet(self.connection, timeline_list_url)
        for timeline in timelines:
            run_time_in_seconds = int(run_time_in_hours) * 60 * 60
            timeline_patch_payload = {"sustainTime": run_time_in_seconds}
            timeline_item_url = self.get_timeline_item_url(timeline.objectID)
            IxLoadUtils.performGenericPatch(self.connection, timeline_item_url, timeline_patch_payload)
        IxLoadUtils.log("Timeline: set sustainTime to %s hours" % run_time_in_hours)
