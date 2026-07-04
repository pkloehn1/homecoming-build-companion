"""Tests for the .mbd (modern JSON) build reader (CP2)."""

from pathlib import Path

import pytest

from coh_engine.buildfile.mbd import Build, load_mbd, parse_mbd

REPO = Path(__file__).resolve().parents[3]
SAMPLES = REPO / "samples" / "builds"
DARK_SHIELD = SAMPLES / "Scrapper - Dark-Shield.mbd"


def test_loads_all_sample_builds() -> None:
    files = sorted(SAMPLES.glob("*.mbd"))
    assert len(files) == 6
    for f in files:
        build = load_mbd(f)
        assert isinstance(build, Build)
        assert build.power_entries, f"{f.name} has no power entries"


def test_meta_and_header_fields() -> None:
    build = load_mbd(DARK_SHIELD)
    assert build.meta.database == "Homecoming"
    assert build.class_name == "Class_Scrapper"
    assert build.origin == "Technology"
    assert build.alignment == "Hero"
    # Top-level Level is the raw character build level (no offset).
    assert build.level == 49
    # LastPower is assigned raw on .mbd load (no -1), per CharacterBuildData.cs:284.
    assert build.last_power == 25
    assert "Scrapper_Melee.Dark_Melee" in build.power_sets


def test_power_and_slot_level_minus_one_offset() -> None:
    build = load_mbd(DARK_SHIELD)
    smite = build.power_entries[0]
    assert smite.power_name == "Scrapper_Melee.Dark_Melee.Smite"
    # Stored Level 1 -> engine 0-based level 0 (character level 1).
    assert smite.level == 0
    first_slot = smite.slot_entries[0]
    # Stored slot Level 1 -> engine 0.
    assert first_slot.level == 0
    assert first_slot.enhancement is not None
    assert first_slot.enhancement.uid == "Crafted_Hecatomb_A"
    assert first_slot.enhancement.relative_level == "PlusFive"
    assert first_slot.enhancement.io_level == 49


def test_empty_slot_enhancement_is_none(tmp_path: Path) -> None:
    mbd = tmp_path / "empty.mbd"
    mbd.write_text(
        """
        {
          "BuiltWith": {"App":"Mids Reborn","Version":"3.8.6.0","Database":"Homecoming","DatabaseVersion":"2026.1.1242"},
          "Level":"50","Class":"Class_Blaster","Origin":"Magic","Alignment":"Hero",
          "Name":"T","Comment":"","PowerSets":["A"],"LastPower":0,
          "PowerEntries":[
            {"PowerName":"A.B.C","Level":2,"StatInclude":true,"ProcInclude":false,
             "VariableValue":0,"InherentSlotsUsed":0,"SubPowerEntries":[],
             "SlotEntries":[{"Level":2,"IsInherent":false,"Enhancement":null,"FlippedEnhancement":null}]}
          ]
        }
        """,
        encoding="utf-8",
    )
    build = load_mbd(mbd)
    slot = build.power_entries[0].slot_entries[0]
    assert slot.enhancement is None
    assert slot.flipped_enhancement is None
    assert slot.level == 1  # stored 2 -> engine 1


def test_legacy_enhancement_key_resolves_to_uid() -> None:
    # The EnhancementDataConverter accepts a legacy "Enhancement" key as the Uid.
    data = {
        "BuiltWith": {"App": "x", "Version": "1.0.0", "Database": "Homecoming", "DatabaseVersion": "1.0.0"},
        "Level": "50",
        "Class": "Class_Blaster",
        "Origin": "Magic",
        "Alignment": "Hero",
        "Name": "T",
        "Comment": "",
        "PowerSets": ["A"],
        "LastPower": 0,
        "PowerEntries": [
            {
                "PowerName": "A.B.C",
                "Level": 1,
                "StatInclude": True,
                "ProcInclude": False,
                "VariableValue": 0,
                "InherentSlotsUsed": 0,
                "SubPowerEntries": [],
                "SlotEntries": [
                    {
                        "Level": 1,
                        "IsInherent": False,
                        "Enhancement": {"Enhancement": "Legacy_Uid_X"},
                        "FlippedEnhancement": None,
                    }
                ],
            }
        ],
    }
    build = parse_mbd(data)
    enh = build.power_entries[0].slot_entries[0].enhancement
    assert enh is not None
    assert enh.uid == "Legacy_Uid_X"
    assert enh.grade == "None"  # default
    assert enh.io_level == 1  # default
    assert enh.relative_level == "Even"  # default


def test_sub_power_entries_parsed(tmp_path: Path) -> None:
    data = {
        "BuiltWith": {"App": "x", "Version": "1.0.0", "Database": "Homecoming", "DatabaseVersion": "1.0.0"},
        "Level": "50",
        "Class": "Class_Blaster",
        "Origin": "Magic",
        "Alignment": "Hero",
        "Name": "T",
        "Comment": "",
        "PowerSets": ["A"],
        "LastPower": 0,
        "PowerEntries": [
            {
                "PowerName": "A.B.C",
                "Level": 1,
                "StatInclude": True,
                "ProcInclude": True,
                "VariableValue": 3,
                "InherentSlotsUsed": 1,
                "SubPowerEntries": [{"PowerName": "Sub1", "StatInclude": True}],
                "SlotEntries": [],
            }
        ],
    }
    build = parse_mbd(data)
    pe = build.power_entries[0]
    assert pe.variable_value == 3
    assert pe.inherent_slots_used == 1
    assert pe.proc_include is True
    assert len(pe.sub_power_entries) == 1
    assert pe.sub_power_entries[0].power_name == "Sub1"
    assert pe.sub_power_entries[0].stat_include is True


def test_enhancement_object_without_uid_is_none() -> None:
    # An enhancement object carrying neither "Uid" nor the legacy "Enhancement"
    # key resolves to an empty slot, not an error.
    data = {
        "BuiltWith": {"App": "x", "Version": "1.0.0", "Database": "Homecoming", "DatabaseVersion": "1.0.0"},
        "Level": "50",
        "Class": "Class_Blaster",
        "Origin": "Magic",
        "Alignment": "Hero",
        "Name": "T",
        "Comment": "",
        "PowerSets": ["A"],
        "LastPower": 0,
        "PowerEntries": [
            {
                "PowerName": "A.B.C",
                "Level": 1,
                "StatInclude": True,
                "ProcInclude": False,
                "VariableValue": 0,
                "InherentSlotsUsed": 0,
                "SubPowerEntries": [],
                "SlotEntries": [
                    {"Level": 1, "IsInherent": False, "Enhancement": {"Grade": "None"}, "FlippedEnhancement": None}
                ],
            }
        ],
    }
    build = parse_mbd(data)
    assert build.power_entries[0].slot_entries[0].enhancement is None


def test_missing_builtwith_raises() -> None:
    with pytest.raises(ValueError, match="BuiltWith"):
        parse_mbd({"Level": "50"})


def test_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_mbd(tmp_path / "nope.mbd")
