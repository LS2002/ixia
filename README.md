# ixia - wrapper for manipulate network, dut, traffic
```
Usage:
build.py [-h] --server SERVER --cluster CLUSTER \
              [--config CONFIG] [--chassis CHASSIS] \
              [--run-rxf RUN_RXF] \
              [--save] \
              [--run] [--wait] [--stop] [--force] [--hours HOURS] [--timeout TIMEOUT]

optional arguments:
  -h, --help         show this help message and exit
  --server SERVER    IxLoad Gateway Server IP
  --cluster CLUSTER  Comma delimited clusters
  --config CONFIG    Path to clusters.json
  --chassis CHASSIS  Path to chassis.json
  --run-rxf RUN_RXF  Run specified RXF only
  --save             Save RXF to C:\Scale\scale-<timestamp>.rxf
  --run              Run test without waiting
  --wait             Wait for result; use along --run
  --stop             Stop test; use after non-waiting --run
  --force            Force reset port; use along --stop
  --hours HOURS      Set hours of the test run; use along --run
  --timeout TIMEOUT  Set httpGet timeout while wait for test results

```
