from utils import IxLoadUtils


class Traffic:
    def __init__(self, connection):
        self.connection = connection.connection
        self.session = connection.session

    def get_traffic_activity_list_url(self, community_id, activity_id=""):
        activity_list_url = "%s/ixload/test/activeTest/communityList/%s/activityList" % (self.session, community_id)
        if activity_id != "":
            return "%s/%s" % (activity_list_url, activity_id)
        else:
            return activity_list_url

    def get_traffic_agent_url(self, community_id, activity_id):
        return "%s/agent" % self.get_traffic_activity_list_url(community_id, activity_id)

    def get_traffic_action_list_url(self, community_id, activity_id, action_id=""):
        action_list_url = "%s/%s/agent/actionList" % (self.get_traffic_activity_list_url(community_id), activity_id)
        if action_id != "":
            return "%s/%s" % (action_list_url, action_id)
        else:
            return action_list_url

    def delete_outdated_traffic(self, cluster_config):
        community_ids = []
        for cluster in cluster_config:
            for cluster_entry in cluster_config[cluster]:
                if cluster_entry["scenario"]["communityList"] not in community_ids:
                    community_ids.append(cluster_entry["scenario"]["communityList"])
        for community_id in community_ids:
            IxLoadUtils.performGenericDelete(self.connection, self.get_traffic_activity_list_url(community_id), {})
        IxLoadUtils.log("Traffic: deleted outdated configs")

    def add_traffic(self, cluster_config):
        for cluster in cluster_config:
            for cluster_entry in cluster_config[cluster]:
                traffic = cluster_entry["activityList"]
                community_id = cluster_entry["scenario"]["communityList"]
                if len(traffic) > 0:
                    activity_list_creation_payload = {"protocolAndType": traffic["protocolAndType"]}
                    activity_id = IxLoadUtils.performGenericPost(self.connection,
                                                                 self.get_traffic_activity_list_url(community_id),
                                                                 activity_list_creation_payload)
                    activity_list_patch_payload = {"name": traffic["name"],
                                                   "enable": traffic["enable"],
                                                   "userObjectiveType": traffic["userObjectiveType"],
                                                   "userObjectiveValue": traffic["userObjectiveValue"]}
                    IxLoadUtils.performGenericPatch(self.connection,
                                                    self.get_traffic_activity_list_url(community_id, activity_id),
                                                    activity_list_patch_payload)

                    agent_patch_payload = {"maxSessions": 1}
                    IxLoadUtils.performGenericPatch(self.connection,
                                                    self.get_traffic_agent_url(community_id, activity_id),
                                                    agent_patch_payload)

                    action_list_creation_payload = {"commandType": traffic["actionList"]["commandType"]}
                    action_id = IxLoadUtils.performGenericPost(self.connection,
                                                               self.get_traffic_action_list_url(community_id,
                                                                                                activity_id),
                                                               action_list_creation_payload)
                    action_list_patch_payload = {"destination": traffic["actionList"]["destination"],
                                                 "commandType": traffic["actionList"]["commandType"],
                                                 "pageObject": traffic["actionList"]["pageObject"]}
                    IxLoadUtils.performGenericPatch(self.connection,
                                                    self.get_traffic_action_list_url(community_id, activity_id,
                                                                                     action_id),
                                                    action_list_patch_payload)
        IxLoadUtils.log("Traffic: added new configs")
