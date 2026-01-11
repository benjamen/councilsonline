#!/usr/bin/env python3
"""
Lodgeick v1.3.0 Performance Benchmark Script

Run this script to measure actual performance improvements.

Usage:
    cd /workspace/development/frappe-bench
    ./env/bin/python /workspace/development/benchmark_v1.3.py
"""

import frappe
import time
from frappe.utils import now


def benchmark_query(description, sql_query, iterations=10):
    """Run a query multiple times and measure average performance"""
    times = []

    for i in range(iterations):
        start = time.time()
        frappe.db.sql(sql_query, as_dict=True)
        end = time.time()
        times.append((end - start) * 1000)  # Convert to ms

    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)

    print(f"\n{description}")
    print(f"  Average: {avg_time:.2f}ms")
    print(f"  Min: {min_time:.2f}ms")
    print(f"  Max: {max_time:.2f}ms")

    # Color code results
    if avg_time < 150:
        status = "✅ EXCELLENT"
    elif avg_time < 250:
        status = "✓ GOOD"
    elif avg_time < 400:
        status = "⚠ ACCEPTABLE"
    else:
        status = "❌ NEEDS OPTIMIZATION"

    print(f"  Status: {status}")

    return avg_time


def verify_indexes():
    """Verify that all expected indexes exist"""
    print("\n" + "="*60)
    print("VERIFYING DATABASE INDEXES")
    print("="*60)

    indexes = frappe.db.sql("""
        SHOW INDEX FROM `tabRequest`
    """, as_dict=True)

    index_names = set([idx['Column_name'] for idx in indexes])

    expected_indexes = {
        'name',  # Primary key
        'workflow_state',
        'request_type',
        'council',
        'assigned_to',
        'requester',
        'submitted_date'
    }

    print(f"\nExpected indexes: {len(expected_indexes)}")
    print(f"Found indexes: {len(index_names)}")

    missing = expected_indexes - index_names
    extra = index_names - expected_indexes

    if missing:
        print(f"\n❌ MISSING INDEXES: {missing}")
    else:
        print("\n✅ All expected indexes present")

    if extra:
        print(f"\nℹ Additional indexes: {extra}")

    print("\nIndex Details:")
    for idx in sorted(indexes, key=lambda x: x['Column_name']):
        print(f"  - {idx['Column_name']}: {idx['Key_name']} ({idx['Index_type']})")


def verify_migration():
    """Verify that all requests have workflow_state set"""
    print("\n" + "="*60)
    print("VERIFYING MIGRATION")
    print("="*60)

    total_requests = frappe.db.count("Request")
    requests_with_state = frappe.db.sql("""
        SELECT COUNT(*)
        FROM `tabRequest`
        WHERE workflow_state IS NOT NULL AND workflow_state != ''
    """)[0][0]

    requests_without_state = total_requests - requests_with_state

    print(f"\nTotal requests: {total_requests}")
    print(f"With workflow_state: {requests_with_state}")
    print(f"Without workflow_state: {requests_without_state}")

    if requests_without_state == 0:
        print("\n✅ Migration successful - all requests have workflow_state")
    else:
        print(f"\n❌ Migration incomplete - {requests_without_state} requests missing workflow_state")

    # Show workflow_state distribution
    state_counts = frappe.db.sql("""
        SELECT workflow_state, COUNT(*) as count
        FROM `tabRequest`
        GROUP BY workflow_state
        ORDER BY count DESC
    """, as_dict=True)

    print("\nWorkflow State Distribution:")
    for state in state_counts:
        print(f"  - {state['workflow_state']}: {state['count']} requests")


def run_benchmarks():
    """Run all performance benchmarks"""
    frappe.init(site="lodgeick.localhost")
    frappe.connect()

    print("="*60)
    print("LODGEICK v1.3.0 PERFORMANCE BENCHMARK")
    print(f"Run at: {now()}")
    print("="*60)

    # Verify indexes and migration first
    verify_indexes()
    verify_migration()

    print("\n" + "="*60)
    print("RUNNING QUERY BENCHMARKS")
    print("="*60)

    results = {}

    # Benchmark 1: List all requests
    results['list_all'] = benchmark_query(
        "1. List all requests (20 records)",
        """
        SELECT r.name, r.request_number, r.workflow_state,
               r.brief_description, r.council, r.submitted_date
        FROM `tabRequest` r
        ORDER BY r.creation DESC
        LIMIT 20
        """
    )

    # Benchmark 2: Filter by workflow_state
    results['filter_state'] = benchmark_query(
        "2. Filter by workflow_state = 'Submitted'",
        """
        SELECT r.name, r.request_number, r.workflow_state
        FROM `tabRequest` r
        WHERE r.workflow_state = 'Submitted'
        LIMIT 20
        """
    )

    # Benchmark 3: Filter by requester
    results['filter_requester'] = benchmark_query(
        "3. Filter by requester (user's requests)",
        """
        SELECT r.name, r.request_number, r.workflow_state
        FROM `tabRequest` r
        WHERE r.requester = 'Administrator'
        LIMIT 20
        """
    )

    # Benchmark 4: Filter by assigned_to
    results['filter_assigned'] = benchmark_query(
        "4. Filter by assigned_to (staff workload)",
        """
        SELECT r.name, r.request_number, r.workflow_state
        FROM `tabRequest` r
        WHERE r.assigned_to = 'Administrator'
        LIMIT 20
        """
    )

    # Benchmark 5: Date range query
    results['date_range'] = benchmark_query(
        "5. Date range query (last 30 days)",
        """
        SELECT r.name, r.request_number, r.submitted_date
        FROM `tabRequest` r
        WHERE r.submitted_date >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        LIMIT 20
        """
    )

    # Benchmark 6: Multi-filter query
    results['multi_filter'] = benchmark_query(
        "6. Multi-filter (state + council + date)",
        """
        SELECT r.name, r.request_number, r.workflow_state
        FROM `tabRequest` r
        WHERE r.workflow_state = 'Assessment'
          AND r.submitted_date >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        LIMIT 20
        """
    )

    # Summary
    print("\n" + "="*60)
    print("BENCHMARK SUMMARY")
    print("="*60)

    # Expected baseline values (pre-v1.3.0)
    baselines = {
        'list_all': 450,
        'filter_state': 380,
        'filter_requester': 290,
        'filter_assigned': 310,
        'date_range': 520,
        'multi_filter': 680
    }

    print("\n| Query | Before v1.3.0 | After v1.3.0 | Improvement |")
    print("|-------|---------------|--------------|-------------|")

    for key, baseline in baselines.items():
        actual = results[key]
        improvement = ((baseline - actual) / baseline) * 100
        status = "✅" if improvement > 40 else "✓" if improvement > 20 else "⚠"
        print(f"| {key:15} | {baseline:6.0f}ms | {actual:7.2f}ms | {status} {improvement:5.1f}% |")

    avg_improvement = sum([
        ((baselines[k] - results[k]) / baselines[k]) * 100
        for k in baselines.keys()
    ]) / len(baselines)

    print(f"\nOverall Average Improvement: {avg_improvement:.1f}%")

    if avg_improvement > 50:
        print("\n🎉 EXCELLENT! Performance improvements exceed expectations!")
    elif avg_improvement > 40:
        print("\n✅ GREAT! Performance improvements meet expectations!")
    elif avg_improvement > 20:
        print("\n✓ GOOD! Performance improved but below target.")
    else:
        print("\n⚠ WARNING! Performance improvements below expectations.")
        print("   Consider running ANALYZE TABLE or checking index usage.")

    print("\n" + "="*60)
    print("BENCHMARK COMPLETE!")
    print("="*60)

    frappe.destroy()


if __name__ == "__main__":
    run_benchmarks()
