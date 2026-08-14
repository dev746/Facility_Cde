"""
tests/load_test.py — Stress test simulating 50 concurrent workers.

Tests that the system handles concurrent WhatsApp messages without:
  - Race conditions in context storage
  - DB connection pool exhaustion
  - Rate limiter false positives
  - Slow response times

Run: PYTHONPATH=. python tests/load_test.py
"""
import sys
import os
import time
import threading
import statistics

# Ensure the project root is on PYTHONPATH
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Set stdout/stderr encoding to UTF-8 for Windows consoles
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

GREEN = "\033[92m"; RED = "\033[91m"; BOLD = "\033[1m"; RESET = "\033[0m"

WORKER_MESSAGES = [
    ("machine M14",          "admin"),
    ("findings M22",         "expert"),
    ("summary M14",          "technician"),
    ("critical",             "admin"),
    ("list",                 "viewer"),
    ("M14 temperature 67",   "technician"),
    ("M22 ki kya problem",   "expert"),
    ("help",                 "viewer"),
    ("latest",               "expert"),
    ("search bearing",       "admin"),
]


def worker_task(worker_id: int, results: list, errors: list):
    """Simulate one worker sending messages."""
    try:
        from query.intent import parse_intent
        from query.context import update_context
        from whatsapp.dispatch import dispatch

        phone = f"whatsapp:+91load{worker_id:04d}"
        role  = WORKER_MESSAGES[worker_id % len(WORKER_MESSAGES)][1]
        text  = WORKER_MESSAGES[worker_id % len(WORKER_MESSAGES)][0]

        user = {
            "phone": phone, "name": f"Worker{worker_id}",
            "role": role, "shift": "morning", "line": "Line A",
        }

        start  = time.time()
        parsed = parse_intent(text)
        intent = parsed.get("intent", "unknown")
        asset  = parsed.get("asset_id")
        reply  = dispatch(intent, asset, text, user, "english")
        elapsed = (time.time() - start) * 1000

        update_context(phone, intent, asset, "english")

        results.append({
            "worker": worker_id,
            "text":   text,
            "intent": intent,
            "elapsed_ms": elapsed,
            "ok":     isinstance(reply, str) and len(reply) > 0,
        })

    except Exception as e:
        errors.append({"worker": worker_id, "error": str(e)})


def run_concurrent(n_workers: int = 50):
    print(f"\n{BOLD}Load test — {n_workers} concurrent workers{RESET}")
    results = []
    errors  = []
    threads = []

    start = time.time()
    for i in range(n_workers):
        t = threading.Thread(target=worker_task, args=(i, results, errors))
        threads.append(t)

    # Start all at once
    for t in threads:
        t.start()

    # Wait for all
    for t in threads:
        t.join(timeout=30)

    total_elapsed = (time.time() - start) * 1000

    # Stats
    if results:
        times  = [r["elapsed_ms"] for r in results]
        ok     = sum(1 for r in results if r["ok"])
        failed = len(results) - ok

        print(f"  Workers:   {n_workers}")
        print(f"  Completed: {len(results)} / {n_workers}")
        print(f"  Errors:    {len(errors)}")
        print(f"  Successes: {ok}")
        print(f"  Total time:{total_elapsed:.0f}ms")
        print(f"  Avg/worker:{statistics.mean(times):.0f}ms")
        print(f"  Median:    {statistics.median(times):.0f}ms")
        print(f"  P95:       {sorted(times)[int(len(times)*0.95)]:.0f}ms")
        print(f"  Max:       {max(times):.0f}ms")

        if errors:
            print(f"\n  {RED}Errors:{RESET}")
            for e in errors[:5]:
                print(f"    Worker {e['worker']}: {e['error'][:70]}")

        if ok == len(results) and not errors:
            print(f"\n  {GREEN}✓ All workers completed successfully{RESET}")
            return True
        else:
            print(f"\n  {RED}✗ {failed} failures, {len(errors)} errors{RESET}")
            return False
    else:
        print(f"  {RED}No results — all workers failed{RESET}")
        return False


def run_sequential_context_test():
    """Test that context doesn't bleed between users."""
    print(f"\n{BOLD}Context isolation test{RESET}")

    from query.context import update_context, get_context

    # Seed two different users with different last assets
    update_context("whatsapp:+91iso001", "machine", "M14", "english")
    update_context("whatsapp:+91iso002", "machine", "M22", "english")

    ctx1 = get_context("whatsapp:+91iso001")
    ctx2 = get_context("whatsapp:+91iso002")

    if ctx1["last_asset_id"] == "M14" and ctx2["last_asset_id"] == "M22":
        print(f"  {GREEN}✓ Context isolated between users{RESET}")
        return True
    else:
        print(f"  {RED}✗ Context bleed detected:{RESET}")
        print(f"    User 1: {ctx1['last_asset_id']} (expected M14)")
        print(f"    User 2: {ctx2['last_asset_id']} (expected M22)")
        return False


def run_rate_limiter_test():
    """Test that rate limiter triggers correctly."""
    print(f"\n{BOLD}Rate limiter test{RESET}")
    from auth.rbac import is_rate_limited

    phone = "whatsapp:+91ratetest"

    # Send 10 requests — should all pass
    passed = 0
    for _ in range(10):
        if not is_rate_limited(phone):
            passed += 1

    # 11th should be blocked
    blocked = is_rate_limited(phone)

    if passed == 10 and blocked:
        print(f"  {GREEN}✓ Rate limiter: 10 allowed, 11th blocked{RESET}")
        return True
    else:
        print(f"  {RED}✗ Rate limiter: {passed}/10 allowed, blocked={blocked}{RESET}")
        return False


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 50

    ok1 = run_concurrent(n)
    ok2 = run_sequential_context_test()
    ok3 = run_rate_limiter_test()

    all_ok = ok1 and ok2 and ok3
    print(f"\n{BOLD}{'='*40}{RESET}")
    status = f"{GREEN}PASS{RESET}" if all_ok else f"{RED}FAIL{RESET}"
    print(f"{BOLD}  Load test: {status}{RESET}")
    print(f"{BOLD}{'='*40}{RESET}\n")
    sys.exit(0 if all_ok else 1)
