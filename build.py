import os
import time
import datetime
import argparse
import json

from ixia_chassis import Chassis
from ixia_dut import DUT
from ixia_connection import Connection
from ixia_network import Network
from ixia_rxf import RXF
from ixia_traffic import Traffic
from ixia_timeline import Timeline
from ixia_run import Run


def get_cluster_json(clusters_json_path, clusters):
    configs = json.loads(open(clusters_json_path).read())
    if clusters != "all":
        clusters_to_keep = clusters.split(",")
        for cluster in configs:
            if cluster not in clusters_to_keep:
                for entry in configs[cluster]:
                    entry["activityList"]["enable"] = False
                    entry["scenario"]["enable"] = 0
    return configs


def get_chassis_json(chassis_json_path):
    return json.loads(open(chassis_json_path).read())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--server', required=True, default='10.0.0.1', help="IxLoad Gateway Server IP")
    parser.add_argument('--cluster', required=True, default="all", help="Comma delimited clusters")
    parser.add_argument('--config', default="config/clusters.json", help="Path to clusters.json")
    parser.add_argument('--chassis', default="config/chassis.json", help="Path to chassis.json")
    parser.add_argument('--run-rxf', help="Run specified RXF only")
    parser.add_argument('--save', action="store_true", help="Save RXF to C:\\Scale\\scale-<timestamp>.rxf")
    parser.add_argument('--run', action="store_true", help="Run test without waiting")
    parser.add_argument('--wait', action="store_true", help="Wait for result; use along --run")
    parser.add_argument('--stop', action="store_true", help="Stop test; use after non-waiting --run")
    parser.add_argument('--force', action="store_true", help="Force reset port; use along --stop")
    parser.add_argument('--hours', default="500", help="Set hours of the test run; use along --run")
    parser.add_argument('--timeout', default="300", help="Set httpGet timeout while wait for test results")
    args = parser.parse_args()
    datetime_stamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H-%M-%S')

    # IxLoad, Connection, Session
    connection = Connection(args.server, 8443, "v1")
    clusters_config = get_cluster_json(args.config, args.cluster)

    # Run Specified RXF Only
    rxf = RXF(connection)
    if args.run_rxf and ".rxf" in args.run_rxf:
        rxf.load_rxf(args.run_rxf)
    else:
        # Network
        network = Network(connection)
        network.delete_outdated_network()
        network.add_network(clusters_config)

        # DUT
        dut = DUT(connection)
        dut.delete_outdated_dut()
        dut.add_dut(clusters_config)

        # Traffic
        traffic = Traffic(connection)
        traffic.delete_outdated_traffic(clusters_config)
        traffic.add_traffic(clusters_config)

        # Timeline
        timeline = Timeline(connection)
        timeline.set_time(args.hours)

    # Chassis
    chassis_config = get_chassis_json(args.chassis)
    chassis = Chassis(connection, chassis_config)
    chassis.delete_outdated_chassis()
    chassis.add_chassis()
    chassis.refresh_connection()
    chassis.assign_port()

    # RXF
    if args.save:
        rxf_path = os.path.split(r"C:\\Scale\\scale-%s.rxf" % datetime_stamp)[1]
        rxf.save_rxf(rxf_path)

    # Test
    run = Run(connection, args.timeout)
    if args.run or (args.run_rxf and ".rxf" in args.run_rxf):
        run.start_test()
        if args.wait:
            run.wait_test()
    if args.stop:
        run.stop_test()
        if args.force:
            chassis.reset_ports(clusters_config)

    # Termination
    connection.shutdown()
