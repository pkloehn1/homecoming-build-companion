# oracle-dump — MidsReborn golden-fixture harness

Test-only C# console harness that loads the MidsReborn Homecoming database **headless**
(no UI) and dumps JSON the Python engine (`src/coh_engine/`) baselines its golden
fixtures against. Mids is the oracle: every numeric claim in the port is validated
against these dumps, per [`docs/engine/mids-port-spec.md`](../../docs/engine/mids-port-spec.md).

## Prerequisites

- .NET SDK 8.0+ (builds with 10.x).
- The MidsReborn fork checked out as a **sibling** of this repo
  (`<repos>/MidsReborn/MidsReborn/MidsReborn.csproj` — the project reference is relative).

## Usage

```bash
dotnet build -c Debug
dotnet run -c Debug --no-build -- <midsreborn-fork>/MidsReborn/Databases/Homecoming ./out
```

Load sequence mirrors `MainModule.LoadDataAsync` (minus graphics); dialogs only fire on
load errors.

## Outputs

| File | Contents |
| --- | --- |
| `version.json` | Homecoming DB version + dump timestamp — every baseline is version-stamped |
| `server_data.json` | `BaseToHit`, `MaxSlots`, `EnableInherentSlotting` |
| `archetypes.json` | Per-AT `Column` (class→column indirection) and all caps (HP/Res/Damage/Recharge/Recovery/Regen/Perception) |
| `maths.json` | `MultED` / `MultTO` / `MultDO` / `MultSO` / `MultHO` / `MultIO` — the ED and grade-effectiveness tables |
| `enhancement_classes.json` | Enhancement class ID/name lookup |
| `power_static_index.json` | `StaticIndex` → `FullName` map (`.mxd` build-file resolution layer) |

## Re-baselining

After any Homecoming DB update in the fork: re-run the dump, refresh
`src/coh_engine/tests/fixtures/oracle/`, and re-run `pytest src/coh_engine/tests`.
`test_oracle_parity.py` fails loudly if the port and the oracle drift.

Float caveat: .NET serializes `float` with shortest-round-trip strings ("0.7"), which
Python parses as float64. Comparisons must quantize both sides through
`coh_engine.maths.f32` — see `test_oracle_parity.py`.

`bin/`, `obj/`, and `out/` are gitignored; the committed baseline lives in the Python
test fixtures, not here.
