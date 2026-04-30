#!/usr/bin/env bash

set -u -o pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
atlas_root="$(cd -- "$script_dir/.." && pwd)"
workspace_root="$(cd -- "$atlas_root/.." && pwd)"

if [[ -x "$workspace_root/.venv/bin/python" ]]; then
    python_bin="$workspace_root/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
    python_bin="$(command -v python3)"
else
    python_bin="$(command -v python)"
fi

tests=(
    "data/asm/qa_logic_memory.asm|160"
    "data/asm/qa_stack_call.asm|16"
    "data/asm/qa_fpu_ops.asm|8"
    "data/asm/qa_org_reloc.asm|42"
    "data/asm/fast_power.asm|1024"
    "data/asm/euclides_mem.asm|6"
    "data/asm/fast_power_pp.asm|1024"
)

failures=0

for entry in "${tests[@]}"; do
    asm_rel="${entry%%|*}"
    expected="${entry##*|}"
    base_name="$(basename "${asm_rel%.asm}")"
    asm_path="$atlas_root/$asm_rel"
    binreloc_path="$script_dir/outputs/assembler/$base_name.binReloc"
    bin_path="$script_dir/outputs/linker/$base_name.bin"
    asm_log="/tmp/${base_name}_asm.log"
    link_log="/tmp/${base_name}_link.log"
    run_log="/tmp/${base_name}_run.log"

    echo "=== $base_name ==="

    if ! "$python_bin" "$script_dir/assembler.py" "$asm_path" >"$asm_log" 2>&1; then
        echo "ASM_FAIL"
        tail -n 10 "$asm_log"
        echo
        failures=$((failures + 1))
        continue
    fi

    if ! "$python_bin" "$script_dir/linker.py" "$binreloc_path" >"$link_log" 2>&1; then
        echo "LINK_FAIL"
        tail -n 10 "$link_log"
        echo
        failures=$((failures + 1))
        continue
    fi

    if printf '1\nq\n' | timeout 30s "$python_bin" "$atlas_root/main.py" "$bin_path" >"$run_log" 2>&1; then
        if ! grep -q '\[OK\] Terminado' "$run_log"; then
            echo "RUN_FAIL"
            tail -n 15 "$run_log"
            echo
            failures=$((failures + 1))
            continue
        fi

        if ! grep -Eq "\\[OUT\\].*= ${expected}$" "$run_log"; then
            echo "ASSERT_FAIL"
            tail -n 15 "$run_log"
            echo
            failures=$((failures + 1))
            continue
        fi

        echo "PASS"
        grep -m1 '\[OK\] Terminado' "$run_log"
        grep '\[OUT\]' "$run_log" | tail -n 1
        echo
        continue
    fi

    run_rc=$?
    if [[ $run_rc -eq 124 ]]; then
        echo "RUN_TIMEOUT"
    else
        echo "RUN_FAIL"
    fi
    tail -n 15 "$run_log"
    echo
    failures=$((failures + 1))
done

if [[ $failures -ne 0 ]]; then
    echo "FAILURES=$failures"
    exit 1
fi

echo "ALL_TESTS_PASSED"