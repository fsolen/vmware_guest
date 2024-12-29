import json
import sys

def analyze_metrics(vm_metrics, host_metrics):
    action_plan = []

    for vm in vm_metrics:
        optimal_host = None
        for host in host_metrics:
            if (
                host['cpu_free'] > vm['cpu_usage'] and
                host['memory_free'] > vm['memory_usage'] and
                host['network_usage'] < 80 and
                host['datastore_free'] > vm['disk_usage'] and
                host['cpu_overcommit'] < 2 and
                vm['is_vnuma_compatible'] and
                host['vm_count'] < host['max_vm_count']
            ):
                if not optimal_host or host['cpu_free'] > optimal_host['cpu_free']:
                    optimal_host = host
        
        if optimal_host:
            action_plan.append({
                "vm_id": vm['vm_id'],
                "source_host": vm['host'],
                "target_host": optimal_host['name']
            })

    return action_plan

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: analyze_metrics.py <vm_metrics.json> <host_metrics.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as vm_file, open(sys.argv[2], 'r') as host_file:
        vm_metrics = json.load(vm_file)
        host_metrics = json.load(host_file)

    plan = analyze_metrics(vm_metrics, host_metrics)
    print(json.dumps(plan, indent=2))
