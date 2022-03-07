from utils import IxLoadUtils
from ixia_network import Network


class Chassis:
    def __init__(self, connection, chassis_config):
        self.connection = connection.connection
        self.session = connection.session
        self.chassis_config = chassis_config
        self.network = Network(connection)
        self.chassis_objectID = None
        self.chassis_id = None

    def get_chassis_list_url(self):
        return "%s/ixload/chassischain/chassisList" % self.session

    def get_chassis_operations_url(self, operation):
        return "%s/%s/operations/%s" % (self.get_chassis_list_url(), self.chassis_objectID, operation)

    def get_chassis_card_list_url(self):
        return "%s/%s/cardList" % (self.get_chassis_list_url(), self.chassis_objectID)

    def get_chassis_card_url(self, card_objectID):
        return "%s/%s" % (self.get_chassis_card_list_url(), card_objectID)

    def get_chassis_port_list_url(self, card_objectID):
        return "%s/portList" % (self.get_chassis_card_url(card_objectID))

    def get_chassis_port_url(self, card_objectID, port_objectID):
        return "%s/%s" % (self.get_chassis_port_list_url(card_objectID), port_objectID)

    def get_port_operations_url(self, card_objectID, port_objectID, operation):
        return "%s/operations/%s" % (self.get_chassis_port_url(card_objectID, port_objectID), operation)

    def delete_outdated_chassis(self):
        IxLoadUtils.performGenericDelete(self.connection, self.get_chassis_list_url(), {})

    def refresh_connection(self):
        IxLoadUtils.performGenericPost(self.connection, self.get_chassis_operations_url("refreshConnection"), {})

    def clear_port_ownership(self, card_objectID, port_objectID):
        IxLoadUtils.performGenericPost(self.connection,
                                       self.get_port_operations_url(card_objectID, port_objectID, "clearOwnership"),
                                       {"force": 1})

    def reboot_port(self, card_objectID, port_objectID):
        IxLoadUtils.performGenericPost(self.connection,
                                       self.get_port_operations_url(card_objectID, port_objectID, "reboot"),
                                       {})

    def add_chassis(self):
        chassis_payload = {"name": self.chassis_config["name"]}
        chassis_objectID = IxLoadUtils.performGenericPost(self.connection, self.get_chassis_list_url(), chassis_payload)
        self.chassis_objectID = chassis_objectID
        chassis_list = IxLoadUtils.performGenericGet(self.connection, self.get_chassis_list_url())
        for chassis in chassis_list:
            if chassis.name == self.chassis_config["name"]:
                self.chassis_id = chassis.id
                break
        IxLoadUtils.log("Chassis: added chassis with id=%s objectID=%s" % (self.chassis_id, self.chassis_objectID))

    def get_ports(self):
        IxLoadUtils.refreshAllChassis(self.connection, self.session)
        chassis_card_list = IxLoadUtils.performGenericGet(self.connection, self.get_chassis_card_list_url())
        chassis_ports = {}
        for card in chassis_card_list:
            ports = IxLoadUtils.performGenericGet(self.connection, self.get_chassis_port_list_url(card.objectID))
            for port in ports:
                chassis_ports.update({port.id: [card.objectID, port.cardId, port.objectID, port.portId]})
        return chassis_ports

    def reset_ports(self, cluster_config):
        network_status_list = {}
        for cluster in cluster_config:
            for cluster_entry in cluster_config[cluster]:
                network_id = cluster_entry["scenario"]["communityList"]
                network_status = cluster_entry['scenario']['enable']
                if network_id not in network_status_list:
                    network_status_list[network_id] = [network_status]
                else:
                    network_status_list[network_id].append(network_status)
        chassis_ports = self.get_ports()
        for network_id in network_status_list:
            if sum(network_status_list[network_id]) != 0:
                for network_entry in self.chassis_config['network']:
                    if int(network_entry["communityList"]) == int(network_id):
                        card_objectID = chassis_ports.get(network_entry['portName'])[0]
                        port_objectID = chassis_ports.get(network_entry['portName'])[2]
                        self.clear_port_ownership(card_objectID, port_objectID)
                        self.reboot_port(card_objectID, port_objectID)
                        break
        IxLoadUtils.log("Chassis: cleared port ownership & rebooted")

    def assign_port(self):
        chassis_ports = self.get_ports()
        for network_entry in self.chassis_config["network"]:
            payload = {"chassisId": self.chassis_id,
                       "cardId": chassis_ports.get(network_entry["portName"])[1],
                       "portId": chassis_ports.get(network_entry["portName"])[3]}
            IxLoadUtils.performGenericPost(self.connection, "%s/%s/network/PortList" % (
                self.network.get_network_community_list_url(), network_entry["communityList"]), payload)
        IxLoadUtils.log("Chassis: assigned chassis ports")