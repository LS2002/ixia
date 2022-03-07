from utils import IxLoadUtils


class Network:
    def __init__(self, connection):
        self.connection = connection.connection
        self.session = connection.session

    def get_network_community_list_url(self):
        return "%s/ixload/test/activeTest/communityList" % self.session;

    def get_network_stack_url(self, community_list_id):
        community_list_url = self.get_network_community_list_url()
        community_list_id_url = "%s/%d" % (community_list_url, community_list_id)
        try:
            IxLoadUtils.performGenericGet(self.connection, community_list_id_url, [404])
        except Exception:
            IxLoadUtils.performGenericPost(self.connection, community_list_url, {})
        return "%s/network/stack" % community_list_id_url

    def get_network_range_list_url(self, community_list_id):
        stack_url = self.get_network_stack_url(community_list_id)
        return IxLoadUtils.getIPRangeListUrlForNetworkObj(self.connection, stack_url)

    def delete_outdated_network(self):
        IxLoadUtils.performGenericDelete(self.connection, self.get_network_community_list_url(), {})

    def create_preceding_network(self, network_id):
        community_url = self.get_network_community_list_url()
        community_list = IxLoadUtils.performGenericGet(self.connection, community_url)
        community_ids = [community.objectID for community in community_list]
        for community_id in range(0, network_id):
            if community_id not in community_ids:
                IxLoadUtils.performGenericPost(self.connection, community_url, {})

    def add_network(self, cluster_config):
        network_valid_name_list = []
        network_status_list = {}
        for cluster in cluster_config:
            for cluster_entry in cluster_config[cluster]:
                network_id = cluster_entry["scenario"]["communityList"]
                self.create_preceding_network(network_id)

                network_status = cluster_entry['scenario']['enable']
                if network_id not in network_status_list:
                    network_status_list[network_id] = [network_status]
                else:
                    network_status_list[network_id].append(network_status)

                network = cluster_entry["scenario"]["network"]
                if len(network) > 0:
                    network_valid_name_list.append(network["name"])
                    range_list_url = self.get_network_range_list_url(cluster_entry["scenario"]["communityList"])
                    range_list_id = IxLoadUtils.performGenericPost(self.connection, range_list_url, {})
                    range_list_payload = {
                        "name": network["name"],
                        "ipAddress": network["ipAddress"],
                        "gatewayAddress": network["gatewayAddress"],
                        "count": network["count"],
                        "ipType": network["ipType"],
                        "prefix": network["cidr"],
                        "incrementBy": network["incrementBy"],
                        "gatewayIncrement": network["gatewayIncrement"]
                    }
                    IxLoadUtils.performGenericPatch(self.connection, "%s/%s" % (range_list_url, range_list_id),
                                                    range_list_payload)
        IxLoadUtils.log("Network: added new configs")

        community_list = IxLoadUtils.performGenericGet(self.connection, self.get_network_community_list_url())
        for community in community_list:
            range_list_url = self.get_network_range_list_url(community.objectID)
            range_content = IxLoadUtils.performGenericGet(self.connection, range_list_url)
            for item in range_content:
                if item.name not in network_valid_name_list:
                    IxLoadUtils.performGenericDelete(self.connection, "%s/%s" % (range_list_url, item.objectID), {})
        IxLoadUtils.log("Network: deleted outdated configs")

        for network_id in network_status_list:
            if sum(network_status_list[network_id]) == 0:
                network_payload = {"enable": 0}
                IxLoadUtils.performGenericPatch(self.connection,
                                                "%s/%s" % (self.get_network_community_list_url(),network_id),
                                                network_payload)
        IxLoadUtils.log("Network: disabled network & traffic")
