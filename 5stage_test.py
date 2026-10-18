from pathlib import Path
import csv
import io
import re
import subprocess
import sys

PROJECT_ROOT = Path(__file__).parent

LOGISIM = PROJECT_ROOT / "tools" / "logisim-evolution.jar"
TEST_DIR = PROJECT_ROOT / "tests" / "integration-custom"

# Halt-counter thresholds for the generated five-stage Logisim test circuits.
# These are debugging values: adjust them here if a test ends before WB.
# Tests omitted from this dictionary keep their generated thresholds.
HALT_CYCLES = {
    "itype_test": 20,
    "btype_test": 48,
    "jtype_test": 24,
    "mem_test": 26,
    "single_beq_test": 32,
}


def set_halt_cycles(circ_path, cycles):
    """Update the halt constant in a generated CS61C run_main circuit.

    Keep original Logisim XML formatting intact, changing only the value of
    the known 16-bit halt constant. Raise an error if the layout changes.
    """
    if not 1 <= cycles <= 0xFFFF:
        raise ValueError(f"Halt threshold must be 1..65535, got {cycles}")

    original = circ_path.read_text(encoding="utf-8")
    pattern = (
        r'(<comp lib="0" loc="\(1630,980\)" name="Constant">\s*'
        r'<a name="value" val=")[^"]+("/>)'
    )
    updated, count = re.subn(
        pattern,
        lambda m: f"{m.group(1)}{hex(cycles)}{m.group(2)}",
        original,
    )
    if count != 1:
        raise RuntimeError(
            f"Expected one halt-counter constant at (1630,980) in {circ_path}; "
            f"found {count}. The circuit template may have changed."
        )

    if updated != original:
        circ_path.write_text(updated, encoding="utf-8")
        print(f"  [HALT] # of cycles: {cycles}")
    else:
        print(f"  [HALT] # of cycles: threshold already {cycles}")

ISA_TESTS = {
    "rtype_test": {
        "x1":  0x00000005,
        "x2":  0x00000002,
        "x5":  0xFFFFFFFD,
        "x6":  0xFFFFFFFF,
        "x7":  0x00000004,
        "x8":  0x00000000,
        "x9":  0x00000007,
        "x10": 0x00000002,
    },

    "itype_test": {
        "x1":  0x00000006,
        "x2":  0xFFFFFFD6,
        "x5":  0x00000000,
        "x6":  0xFFFFFFF9,
        "x7":  0x00000001,
        "x8":  0x3FFFFFF5,
        "x9":  0xFFFFFFF5,
        "x10": 0x00000005,
    },

    "btype_test": {
    "x1":  0x00000000,
    "x2":  0x00000000,
    "x5":  0x00000005, 
    "x6":  0x00000007, 
    "x7":  0xFFFFFFFF, 
    "x8":  0x00000006, 
    "x9":  0x00000005, 
    "x10": 0x00000000,  
},

    "jtype_test": {
        "x1":  0x00000018,
        "x2":  0x00000000,
        "x5":  0x00000000,
        "x6":  0x0000001C,
        "x7":  0x00000000,
        "x8":  0x00000005,
        "x9":  0x00000006,
        "x10": 0x00000009,
    },

    "mem_test": {
        "x1":  0x00000000,
        "x2":  0x00000000,
        "x5":  0x12345678,
        "x6":  0x00000078,
        "x7":  0x00000056,
        "x8":  0xFFFFFFFF,
        "x9":  0xFFFFFFFF,
        "x10": 0x00005678,
    },
    "single_beq_test": {
        "x1":  0x00000000,
        "x2":  0x00000000,
        "x5":  0x00000005,  # t0
        "x6":  0x00000000,
        "x7":  0x00000000,
        "x8":  0x00000001,  # s0
        "x9":  0x00000005,  # s1
        "x10": 0x00000000,  # a0: must remain zero
    },
}

MICROARCH_TESTS = {
    "5s_basic_pipeline_test": {
        "x5":  0x00000005,
        "x6":  0x00000007,
        "x7":  0x0000000C,
    },
}

def run_logisim(test_name):
    circ = TEST_DIR / f"{test_name}.circ"

    if not circ.exists():
        print(f"[ERROR] Missing circuit: {circ}")
        print("Run: bash test.sh create_custom")
        sys.exit(1)

    if test_name in HALT_CYCLES:
        set_halt_cycles(circ, HALT_CYCLES[test_name])

    result = subprocess.run(
        [
            "java",
            "-jar",
            str(LOGISIM),
            "-tty",
            "table,binary,csv",
            str(circ),
        ],
        text=True,
        capture_output=True,
    )

    if result.returncode != 0:
        print("[ERROR] Logisim failed")
        print(result.stderr)
        sys.exit(1)

    rows = list(csv.reader(io.StringIO(result.stdout)))

    if not rows:
        print("[ERROR] Logisim produced no trace")
        sys.exit(1)

    return rows


def binary_to_int(value):
    # Detect Logisim undefined/error values.
    if any(c not in "01" for c in value):
        return None

    return int(value, 2)


def final_state(rows):
    row = rows[-1]

    return {
        "x1": binary_to_int(row[0]),
        "x2": binary_to_int(row[1]),
        "x5": binary_to_int(row[2]),
        "x6": binary_to_int(row[3]),
        "x7": binary_to_int(row[4]),
        "x8": binary_to_int(row[5]),
        "x9": binary_to_int(row[6]),
        "x10": binary_to_int(row[7]),
        "pc": binary_to_int(row[8]),
        "instruction": binary_to_int(row[9]),
        "time": binary_to_int(row[10]),
    }


def check_registers(state, expected):
    passed = True

    for reg, expected_value in expected.items():
        actual = state[reg]

        if actual == expected_value:
            print(f"  [PASS] {reg} = 0x{actual:08x}")
        elif actual is None:
            print(
                f"  [FAIL] {reg}: expected 0x{expected_value:08x}, "
                f"got undefined"
            )
            passed = False
        else:
            print(
                f"  [FAIL] {reg}: expected 0x{expected_value:08x}, "
                f"got 0x{actual:08x}"
            )
            passed = False

    return passed


def run_test_group(group_name, tests):
    print(group_name)
    print("-" * 40)

    passed_count = 0

    for test_name, expected in tests.items():
        print(f"Running {test_name}...")

        rows = run_logisim(test_name)
        state = final_state(rows)

        passed = check_registers(state, expected)

        if passed:
            print(f"[PASS] {test_name}")
            passed_count += 1
        else:
            print(f"[FAIL] {test_name}")

        print()

    return passed_count, len(tests)


def main():
    isa_passed, isa_total = run_test_group(
        "ISA VERIFICATION",
        ISA_TESTS
    )

    micro_passed, micro_total = run_test_group(
        "5-STAGE MICROARCHITECTURE",
        MICROARCH_TESTS
    )

    passed = isa_passed + micro_passed
    total = isa_total + micro_total

    print("=" * 40)
    print(f"{passed}/{total} tests passed")

    sys.exit(0 if passed == total else 1)

if __name__ == "__main__":
    main()