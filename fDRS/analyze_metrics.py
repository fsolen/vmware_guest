import json
import sys

def analyze_metrics(vm_metrics, host_metrics):
    action_plan = []

    def calculate_host_load_score(host):
        cpu_load = host['cpu_usage'] / host['cpu_capacity']
        memory_load = host['memory_usage'] / host['memory_capacity']
        network_load = host['network_usage'] / 100
        disk_io_load = host['disk_io_usage'] / host['disk_io_capacity']
        datastore_load = 1 - (host['datastore_free'] / host['datastore_capacity'])

        return (
            0.2 * cpu_load +
            0.4 * memory_load +
            0.1 * network_load +
            0.1 * disk_io_load +
            0.8 * datastore_load
        )

    for vm in vm_metrics:
        optimal_host = None
        lowest_load_score = float('inf')

        for host in host_metrics:
            current_host_score = calculate_host_load_score(host)

            if (
                host['cpu_free'] > vm['cpu_usage'] and
                host['memory_free'] > vm['memory_usage'] and
                host['network_usage'] < 80 and
                host['datastore_free'] > vm['disk_usage'] and
                host['cpu_overcommit'] < 3 and
                vm['is_vnuma_compatible'] and
                host['vm_count'] < host['max_vm_count']
            ):
                if current_host_score < lowest_load_score:
                    optimal_host = host
                    lowest_load_score = current_host_score

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
