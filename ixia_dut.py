import ipaddress
from utils import IxLoadUtils


class DUT:
    def __init__(self, connection):
        self.connection = connection.connection
        self.session = connection.session

    def get_dut_list_url(self):
        return "%s/ixload/test/activeTest/dutList" % self.session

    def get_dut_url(self, dut_id):
        return "%s/%s" % (self.get_dut_list_url(), dut_id)

    def get_dut_network_range_list_url(self, dut_id):
        return "%s/dutConfig/networkRangeList" % self.get_dut_url(dut_id)

    @staticmethod
    def get_subnet_of_ip_cidr(ip, cidr):
        return ipaddress.ip_network("%s/%s" % (ip, cidr), strict=False)

    def delete_outdated_dut(self):
        IxLoadUtils.performGenericDelete(self.connection, self.get_dut_list_url(), {})

    def add_dut(self, cluster_config):
        dut_valid_network_list = []
        for cluster in cluster_config:
            for cluster_entry in cluster_config[cluster]:
                dut = cluster_entry["dut"]
                subnet_count = dut["subnetCount"]
                dut_ip = ipaddress.ip_address(dut["firstIp"].split("/")[0])
                dut_ip_count = dut["ipCount"]
                dut_cidr = dut["firstIp"].split("/")[1]
                dut_network = self.get_subnet_of_ip_cidr(str(dut_ip), dut_cidr)
                dut_network_ip_count = dut_network.num_addresses
                dut_network_netmask = dut_network.netmask
                dut_property = {"name": dut["name"], "type": dut["type"]}
                dut_id = IxLoadUtils.addDUT(self.connection, self.session, dut_property)

                for network_range_list_id in range(0, int(subnet_count)):
                    dut_valid_network_list.append(str(self.get_subnet_of_ip_cidr(str(dut_ip), dut_cidr)))
                    dut_configs = {"post": {
                        "network.%s" % str(network_range_list_id): {
                            "firstIp": str(dut_ip),
                            "networkMask": str(dut_network_netmask),
                            "ipCount": str(dut_ip_count)
                        }}}
                    dut_url = self.get_dut_url(dut_id)
                    IxLoadUtils.editDutConfig(self.connection, dut_url, dut_configs)
                    dut_ip += dut_network_ip_count
        IxLoadUtils.log("DUT: added new ones")

        dut_list = IxLoadUtils.performGenericGet(self.connection, self.get_dut_list_url())
        for dut in dut_list:
            range_list_url = self.get_dut_network_range_list_url(dut.objectID)
            range_content = IxLoadUtils.performGenericGet(self.connection, range_list_url)
            for item in range_content:
                if str(self.get_subnet_of_ip_cidr(item.firstIp,
                                                  item.networkMask if len(item.firstIp) <= 15 else 64)
                       ) not in dut_valid_network_list:
                    IxLoadUtils.log("DUT: deleting item.firstIp %s %s %s" % (item.firstIp, "item.networkMask =", item.networkMask))
                    IxLoadUtils.performGenericDelete(self.connection, "%s/%s" % (range_list_url, item.objectID), {})
        IxLoadUtils.log("DUT: deleted outdated items")
