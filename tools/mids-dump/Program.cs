// MidsDump — test-only harness that loads the MidsReborn Homecoming database
// headless (no UI) and dumps the reference data the Python port (src/coh_engine)
// baselines its golden fixtures against.
//
// Usage: MidsDump <databases-dir> <output-dir>
//   <databases-dir>  e.g. <midsreborn-fork>/MidsReborn/Databases/Homecoming
//   <output-dir>     directory to write the JSON dumps into (created if missing)
//
// Load sequence mirrors MainModule.LoadDataAsync (MidsReborn MainModule.cs:145-218),
// minus graphics. Dialogs only fire on load errors.

using System.Text.Json;
using System.Text.Json.Serialization;
using Mids_Reborn;
using Mids_Reborn.Core;
using Mids_Reborn.Core.Base.Data_Classes;
using Mids_Reborn.Core.Base.Master_Classes;
using Mids_Reborn.Core.BuildFile;

namespace MidsDump;

internal static class Program
{
    private static readonly JsonSerializerOptions JsonOpts = new()
    {
        WriteIndented = true,
        DefaultIgnoreCondition = JsonIgnoreCondition.Never,
    };

    [STAThread]
    private static int Main(string[] args)
    {
        if (args.Length < 2)
        {
            Console.Error.WriteLine("usage: MidsDump <databases-dir> <output-dir>");
            return 2;
        }

        var dataPath = Path.GetFullPath(args[0]);
        var outDir = Path.GetFullPath(args[1]);
        if (!Directory.Exists(dataPath))
        {
            Console.Error.WriteLine($"E01: databases dir not found: {dataPath}");
            return 2;
        }
        Directory.CreateDirectory(outDir);

        // Mids' loaders expect a trailing separator when combining paths.
        if (!dataPath.EndsWith(Path.DirectorySeparatorChar))
        {
            dataPath += Path.DirectorySeparatorChar;
        }

        ConfigData.Initialize();

        if (!DatabaseAPI.LoadServerData(dataPath))
        {
            Console.Error.WriteLine("E02: LoadServerData failed");
            return 1;
        }

        DatabaseAPI.Database.AttribMods = new Modifiers();
        if (!DatabaseAPI.Database.AttribMods.Load(dataPath))
        {
            Console.Error.WriteLine("E03: AttribMods.Load failed");
            return 1;
        }

        DatabaseAPI.LoadTypeGrades(dataPath);

        if (!DatabaseAPI.LoadLevelsDatabase(dataPath))
        {
            Console.Error.WriteLine("E04: LoadLevelsDatabase failed");
            return 1;
        }

        if (!DatabaseAPI.LoadMainDatabase(dataPath))
        {
            Console.Error.WriteLine("E05: LoadMainDatabase failed");
            return 1;
        }

        if (!DatabaseAPI.LoadMaths(dataPath))
        {
            Console.Error.WriteLine("E06: LoadMaths failed");
            return 1;
        }

        if (!DatabaseAPI.LoadEffectIdsDatabase(dataPath))
        {
            Console.Error.WriteLine("E07: LoadEffectIdsDatabase failed");
            return 1;
        }

        if (!DatabaseAPI.LoadEnhancementClasses(dataPath))
        {
            Console.Error.WriteLine("E08: LoadEnhancementClasses failed");
            return 1;
        }

        DatabaseAPI.LoadEnhancementDb(dataPath);
        DatabaseAPI.LoadOrigins(dataPath);
        DatabaseAPI.LoadSalvage(dataPath);
        DatabaseAPI.LoadRecipes(dataPath);
        DatabaseAPI.LoadReplacementTable();
        DatabaseAPI.MatchAllIDs();
        DatabaseAPI.AssignSetBonusIndexes();
        DatabaseAPI.AssignRecipeIDs();

        // An empty character context so computed effect getters (e.g. Probability,
        // which parses an expression against character state) don't dereference a
        // null MidsContext.Character during the DB-level set_bonus_powers dump.
        MainModule.MidsController.Toon = new clsToonX();

        DumpVersion(outDir);
        DumpServerData(outDir);
        DumpArchetypes(outDir);
        DumpMaths(outDir);
        DumpEnhancementClasses(outDir);
        DumpEnhancements(outDir);
        DumpLegalityProbe(outDir);
        DumpEnhancementEffects(outDir);
        DumpEnhancementSets(outDir);
        DumpSetBonusPowers(outDir);
        DumpPowerIndex(outDir);
        DumpEnums(outDir);
        DumpConfig(outDir);

        // Optional third arg: a directory of .mbd sample builds. Each is loaded
        // through Mids and re-saved as a .mxd share block, giving the Python port
        // real Mids-produced .mxd fixtures to validate its reader against.
        // Pass "-" to skip.
        if (args.Length >= 3 && args[2] != "-")
        {
            ExportMxdBuilds(Path.GetFullPath(args[2]), outDir);
        }

        // Optional fourth arg: a directory of parity-build .mbd files. Each is
        // loaded through Mids, recomputed via GenerateBuffedPowerArray, and dumped
        // as builds/<name>/{powers_effects,totals}.json — the reference fixtures
        // the Python base-totals math is validated against.
        if (args.Length >= 4)
        {
            var failures = DumpParityBuilds(Path.GetFullPath(args[3]), outDir);
            if (failures > 0)
            {
                // Fail loudly: a silent OK on a bad re-baseline leaves the Python
                // parity suite validating against stale or missing fixtures.
                Console.Error.WriteLine($"E14: {failures} parity build(s) failed; dumps are incomplete");
                return 1;
            }
        }

        Console.WriteLine($"OK: dumps written to {outDir}");
        return 0;
    }

    private static void DumpEnums(string outDir)
    {
        // Name -> ordinal for every enum the engine indexes arrays by (Totals.Def
        // by eDamage, _selfBuffs.Effect by eEffectType/eStatType, ...). The Python
        // port must never guess these orderings.
        var enums = new Dictionary<string, Dictionary<string, int>>();
        var enumTypes = new[]
        {
            typeof(Enums.eEffectType), typeof(Enums.eDamage), typeof(Enums.eMez),
            typeof(Enums.eToWho), typeof(Enums.ePvX), typeof(Enums.eAspect),
            typeof(Enums.eAttribType), typeof(Enums.eEffectClass), typeof(Enums.eStacking),
            typeof(Enums.eSuppress), typeof(Enums.ePowerType), typeof(Enums.eSpecialCase),
            typeof(Enums.eStatType),
            // Enhancement-value pipeline: the port resolves a slotted
            // enhancement's aspect (eEnhance), grade/relative-level/type, and ED
            // schedule by ordinal from these maps.
            typeof(Enums.eEnhance), typeof(Enums.eEnhGrade), typeof(Enums.eEnhRelative),
            typeof(Enums.eType), typeof(Enums.eSchedule),
            // Set-bonus subsystem: eSetType maps an EnhancementSet to the powers
            // that accept it (Power.SetTypes). ePvX (tier-bonus PvMode gate) is
            // already dumped above.
            typeof(Enums.eSetType),
        };
        foreach (var t in enumTypes)
        {
            var values = new Dictionary<string, int>();
            foreach (var v in Enum.GetValues(t))
            {
                values[v.ToString()!] = Convert.ToInt32(v);
            }
            enums[t.Name] = values;
        }
        WriteJson(outDir, "enums.json", enums);
    }

    private static void DumpConfig(string outDir)
    {
        // The config state the totals were computed under. The Python port pins
        // its assumptions (PvE mode, no suppression, level-50 build) to this dump.
        var cfg = MidsContext.Config;
        WriteJson(outDir, "config.json", new
        {
            Suppression = (int)cfg.Suppression,
            cfg.Inc.DisablePvE,
            cfg.ForceLevel,
            cfg.ScalingToHit,
        });
    }

    // Returns the number of parity builds that failed to load; Main turns a
    // non-zero count into a non-zero exit so a bad re-baseline is never masked.
    private static int DumpParityBuilds(string buildsDir, string outDir)
    {
        if (!Directory.Exists(buildsDir))
        {
            Console.Error.WriteLine($"E12: parity-builds dir not found: {buildsDir}");
            return 1;
        }

        var failures = 0;
        var byName = new Dictionary<string, string>();
        foreach (var mbdPath in Directory.EnumerateFiles(buildsDir, "*.mbd", SearchOption.AllDirectories))
        {
            var toon = new clsToonX();
            MainModule.MidsController.Toon = toon;
            if (!BuildManager.Instance.LoadFromFile(mbdPath))
            {
                Console.Error.WriteLine($"E13: LoadFromFile failed for {mbdPath}");
                failures++;
                continue;
            }

            toon.GenerateBuffedPowerArray();
            var name = Path.GetFileNameWithoutExtension(mbdPath);
            byName[name] = mbdPath;
            DumpOneBuild(Path.Combine(outDir, "builds", name), toon);
        }

        failures += DumpExemplarVariants(byName, outDir);
        return failures;
    }

    private static void DumpOneBuild(string buildDir, clsToonX toon)
    {
        Directory.CreateDirectory(buildDir);
        DumpBuildPowersEffects(buildDir, toon);
        DumpBuildSlots(buildDir, toon);
        DumpBuildEnhancedPowers(buildDir, toon);
        DumpBuildSetBonusVirtualPower(buildDir, toon);
        DumpBuildTotals(buildDir, toon);
    }

    // Builds recomputed at a lowered ForceLevel: the exemplar parity fixtures. At a
    // low ForceLevel, powers picked above it drop their set bonuses (pick Level >
    // ForceLevel) and slots placed at/above it stop contributing — the CP6 exemplar
    // gate the port threads through config.force_level. No -3 retention (Mids gates
    // purely on pick Level <= ForceLevel).
    private static readonly (string Build, int ForceLevel)[] ExemplarVariants =
    {
        ("shield_scrapper_set_bonuses", 25),
    };

    private static int DumpExemplarVariants(IReadOnlyDictionary<string, string> byName, string outDir)
    {
        var failures = 0;
        var savedForceLevel = MidsContext.Config.ForceLevel;
        foreach (var (buildName, forceLevel) in ExemplarVariants)
        {
            if (!byName.TryGetValue(buildName, out var mbdPath))
            {
                Console.Error.WriteLine($"E21: exemplar-variant source build not found: {buildName}");
                failures++;
                continue;
            }

            var toon = new clsToonX();
            MainModule.MidsController.Toon = toon;
            if (!BuildManager.Instance.LoadFromFile(mbdPath))
            {
                Console.Error.WriteLine($"E13: LoadFromFile failed for {mbdPath} (exemplar variant)");
                failures++;
                continue;
            }

            MidsContext.Config.ForceLevel = forceLevel;
            toon.GenerateBuffedPowerArray();
            DumpOneBuild(Path.Combine(outDir, "builds", $"{buildName}_exemplar{forceLevel}"), toon);
        }

        MidsContext.Config.ForceLevel = savedForceLevel;
        return failures;
    }

    private static void DumpBuildPowersEffects(string buildDir, clsToonX toon)
    {
        // The build's resolved DB powers with the full magnitude-driving effect
        // field set. The Python port computes base totals from THESE records; the
        // enum-valued fields are dumped as names (enums.json maps them to ordinals).
        //
        // Limitation: this dumps the raw master-DB power (db.Power[NIDPower]),
        // whose Effects are the pre-assembly set. GBPA assembly can add effects
        // that never appear here — sub-power absorption (GBPA_AddSubPowerEffects)
        // and power-override redirects (GBPA_ApplyPowerOverride). The paired
        // totals.json comes from GenerateBuffedPowerArray, so for a build with
        // such powers the two would disagree. No committed fixture uses one; a
        // fixture that does will need this widened to the assembled _buffedPowers.
        var db = DatabaseAPI.Database;
        var powers = new List<object>();
        for (var i = 0; i < toon.CurrentBuild.Powers.Count; i++)
        {
            var entry = toon.CurrentBuild.Powers[i];
            if (entry == null || entry.NIDPower < 0)
            {
                continue;
            }

            var pw = db.Power[entry.NIDPower];
            if (pw == null)
            {
                continue;
            }

            powers.Add(new
            {
                BuildIndex = i,
                entry.NIDPower,
                pw.FullName,
                pw.StaticIndex,
                PowerType = pw.PowerType.ToString(),
                pw.ForcedClass,
                pw.ClickBuff,
                // pw.Level is the DB minimum pick level; PickLevel is the level this
                // build actually took the power (PowerEntry.Level). The set-bonus
                // exemplar gate (Build.cs:1160) uses the PICK level, not the DB
                // minimum — the two coincide at ForceLevel 50 but diverge under
                // exemplar (a power whose DB min is 14 but picked at 30 drops at
                // ForceLevel 25). Dump both; the port gates on PickLevel.
                pw.Level,
                PickLevel = entry.Level,
                pw.EndCost,
                pw.ActivatePeriod,
                pw.ToggleCost,
                pw.VariableEnabled,
                entry.StatInclude,
                entry.VariableValue,
                // The enhancement set types this power accepts (Power.SetTypes,
                // the raw eSetType ordinals as List<int>). An IO set is slottable
                // here only if its SetType ordinal is in this list — the power<->set
                // acceptance map the legality layer (and the set-bonus tally's
                // validity assumption) rests on. Empty means the power takes no set
                // IOs (e.g. Battle Agility). eSetType names are in enums.json.
                pw.SetTypes,
                // The enhancement class IDs this power accepts (Power.Enhancements,
                // int[] of EnhancementClasses[..].ID). A standard/generic IO is legal
                // here only if one of its ClassIds is in this list (IsEnhancementValid);
                // the standard-IO half of legality CP6 adds atop CP5's set-type gate.
                pw.Enhancements,
                Effects = pw.Effects.Select((fx, fxIdx) => SerializeEffect(fx, fxIdx)).ToList(),
            });
        }
        WriteJson(buildDir, "powers_effects.json", powers);
    }

    // Shared effect serializer: the full magnitude-driving field set the Python
    // port's effect model reads. Used for build powers (powers_effects.json) and
    // the referenced set_bonus_powers the virtual power clones effects from.
    private static object SerializeEffect(IEffect fx, int idx)
    {
        return new
        {
            Index = idx,
            EffectType = fx.EffectType.ToString(),
            DamageType = fx.DamageType.ToString(),
            MezType = fx.MezType.ToString(),
            ETModifies = fx.ETModifies.ToString(),
            fx.Scale,
            fx.nMagnitude,
            fx.nDuration,
            AttribType = fx.AttribType.ToString(),
            Aspect = fx.Aspect.ToString(),
            fx.ModifierTable,
            fx.nModifierTable,
            ToWho = fx.ToWho.ToString(),
            PvMode = fx.PvMode.ToString(),
            Stacking = fx.Stacking.ToString(),
            Suppression = (int)fx.Suppression,
            fx.Buffable,
            fx.Resistible,
            fx.IgnoreED,
            fx.IgnoreScaling,
            fx.VariableModified,
            fx.BaseProbability,
            fx.Probability,
            fx.ProcsPerMinute,
            fx.Ticks,
            fx.DelayedTime,
            EffectClass = fx.EffectClass.ToString(),
            SpecialCase = fx.SpecialCase.ToString(),
            fx.nIDClassName,
            fx.Absorbed_Effect,
            Absorbed_PowerType = fx.Absorbed_PowerType.ToString(),
            fx.Absorbed_Class_nID,
            ActiveConditionalsCount = fx.ActiveConditionals?.Count ?? 0,
            ExprMagnitude = fx.Expressions?.Magnitude ?? "",
            ExprDuration = fx.Expressions?.Duration ?? "",
            ExprProbability = fx.Expressions?.Probability ?? "",
            fx.DisplayPercentage,
        };
    }

    // Light serializer for the set-bonus virtual-power golden: the structural
    // identity the port keys effects by, plus the resolved Mag/BuffedMag. The
    // port assembles its virtual power by cloning set_bonus_powers effects (full
    // field set there) and validates the sequence, count, and magnitude here.
    private static object SerializeVirtualEffect(IEffect fx, int idx)
    {
        return new
        {
            Index = idx,
            EffectType = fx.EffectType.ToString(),
            DamageType = fx.DamageType.ToString(),
            MezType = fx.MezType.ToString(),
            ETModifies = fx.ETModifies.ToString(),
            fx.Mag,
            fx.BuffedMag,
        };
    }

    private static void DumpBuildSlots(string buildDir, clsToonX toon)
    {
        // The resolved per-power slot layout: for each build power, its SlotEntry
        // array as Mids resolved it (I9Slot already clamped Grade/IOLevel and
        // resolved the UID to an Enh nID). BuildIndex matches powers_effects.json.
        // The port aggregates enhancement value per aspect over these slots,
        // gating each by Enh > -1 and Level < ForceLevel (clsToonX.cs:1751), so
        // Level here is Mids' internal (0-based) slot-placement level, dumped raw.
        var builds = new List<object>();
        for (var i = 0; i < toon.CurrentBuild.Powers.Count; i++)
        {
            var entry = toon.CurrentBuild.Powers[i];
            if (entry == null || entry.NIDPower < 0 || entry.Slots == null)
            {
                continue;
            }

            builds.Add(new
            {
                BuildIndex = i,
                Slots = entry.Slots.Select(s => new
                {
                    s.Level,
                    s.IsInherent,
                    s.Enhancement.Enh,
                    Grade = (int)s.Enhancement.Grade,
                    GradeName = s.Enhancement.Grade.ToString(),
                    s.Enhancement.IOLevel,
                    RelativeLevel = (int)s.Enhancement.RelativeLevel,
                    RelativeLevelName = s.Enhancement.RelativeLevel.ToString(),
                }).ToList(),
            });
        }
        WriteJson(buildDir, "slots.json", builds);
    }

    private static void DumpBuildEnhancedPowers(string buildDir, clsToonX toon)
    {
        // The per-power enhanced (buffed) values GenerateBuffedPowerArray produced:
        // GetEnhancedPower(i) returns _buffedPowers[i] with the enhancement
        // multipliers already applied (RechargeTime/EndCost divided by their
        // multiplier, Range multiplied, each effect's Math_Mag = base * mult).
        // This is the per-power, per-aspect float32 reference the enhancement pipeline is
        // validated against (e.g. Hasten recharge 0.9908 surfaces as a reduced
        // RechargeTime, never in Totals).
        var powers = new List<object>();
        for (var i = 0; i < toon.CurrentBuild.Powers.Count; i++)
        {
            var entry = toon.CurrentBuild.Powers[i];
            if (entry == null || entry.NIDPower < 0)
            {
                continue;
            }

            var buffed = toon.GetEnhancedPower(i);
            if (buffed == null)
            {
                continue;
            }

            // Base (unenhanced, assembled) scalars: the port multiplies these by
            // its computed enhancement multipliers and must reproduce `buffed`.
            // Dumping them keeps the per-power parity assertion free of magic
            // base constants.
            var basePower = toon.GetBasePower(i);

            powers.Add(new
            {
                BuildIndex = i,
                buffed.FullName,
                buffed.Accuracy,
                buffed.AccuracyMult,
                buffed.EndCost,
                buffed.InterruptTime,
                buffed.Range,
                buffed.RechargeTime,
                Base = basePower == null
                    ? null
                    : new
                    {
                        basePower.Accuracy,
                        basePower.EndCost,
                        basePower.InterruptTime,
                        basePower.Range,
                        basePower.RechargeTime,
                    },
                Effects = buffed.Effects.Select((fx, fxIdx) => new
                {
                    Index = fxIdx,
                    // Structural identity so the parity test matches effects by
                    // (type, damage, mez, ETModifies) rather than array position:
                    // GBPA assembly can reorder/trim the buffed effect array
                    // relative to the raw powers_effects dump.
                    EffectType = fx.EffectType.ToString(),
                    DamageType = fx.DamageType.ToString(),
                    MezType = fx.MezType.ToString(),
                    ETModifies = fx.ETModifies.ToString(),
                    fx.Math_Mag,
                    fx.Math_Duration,
                }).ToList(),
            });
        }
        WriteJson(buildDir, "enhanced_powers.json", powers);
    }

    private static void DumpBuildTotals(string buildDir, clsToonX toon)
    {
        WriteJson(buildDir, "totals.json", new
        {
            Class = toon.Archetype?.ClassName,
            toon.Level,
            Totals = MapTotals(toon.Totals),
            TotalsCapped = MapTotals(toon.TotalsCapped),
        });
    }

    private static object MapTotals(Character.TotalStatistics t)
    {
        return new
        {
            t.Def,
            t.Res,
            t.Mez,
            t.MezRes,
            t.DebuffRes,
            t.Elusivity,
            t.HPRegen,
            t.HPMax,
            t.Absorb,
            t.EndRec,
            t.EndUse,
            t.EndMax,
            t.RunSpd,
            t.MaxRunSpd,
            t.JumpSpd,
            t.MaxJumpSpd,
            t.FlySpd,
            t.MaxFlySpd,
            t.JumpHeight,
            t.StealthPvE,
            t.StealthPvP,
            t.ThreatLevel,
            t.Perception,
            t.BuffHaste,
            t.BuffAcc,
            t.BuffToHit,
            t.BuffDam,
            t.BuffEndRdx,
            t.BuffRange,
            t.BuffHeal,
        };
    }

    private static void DumpEnhancements(string outDir)
    {
        // StaticIndex -> {UID, TypeID}: the map the .mxd slot reader needs to know
        // how many bytes follow each enhancement reference (the TypeID switch in
        // ReadSlotData). The in-memory nID is the array index.
        //
        // The legality layer (CP6) additionally reads:
        //   ClassIds  - Enhancement.ClassID[] resolved from EnhancementClasses index
        //               to the class .ID (int); Power.IsEnhancementValid tests these
        //               against Power.Enhancements. Resolving here keeps the port from
        //               needing the EnhancementClasses index table at check time.
        //   SubTypeId - GetValidEnhancements' subtype gate (0 = wildcard).
        //   Unique / MutExId / Superior / LongName - Build.EnhancementTest's build-wide
        //               unique / mutual-exclusion (superior-attuned, stealth) rules.
        var db = DatabaseAPI.Database;
        var classes = db.EnhancementClasses;
        var enhancements = db.Enhancements
            .Select((e, nid) => (e, nid))
            .Where(t => t.e != null)
            .Select(t => new
            {
                Nid = t.nid,
                t.e.StaticIndex,
                t.e.UID,
                t.e.LongName,
                TypeId = (int)t.e.TypeID,
                TypeName = t.e.TypeID.ToString(),
                SubTypeId = t.e.SubTypeID,
                // The owning set (-1 for non-set IOs); the SetO legality branch
                // resolves the set's SetType via this and tests it against Power.SetTypes.
                t.e.nIDSet,
                // ClassID indexes EnhancementClasses; the ID we test against
                // Power.Enhancements is EnhancementClasses[idx].ID. Guard the index
                // (a stray -1/out-of-range entry contributes no class).
                ClassIds = (t.e.ClassID ?? Array.Empty<int>())
                    .Where(idx => idx >= 0 && idx < classes.Length)
                    .Select(idx => classes[idx].ID)
                    .ToList(),
                t.e.Unique,
                MutExId = (int)t.e.MutExID,
                MutExName = t.e.MutExID.ToString(),
                t.e.Superior,
            })
            .ToList();
        WriteJson(outDir, "enhancements.json", enhancements);
    }

    // The (power, enhancement) pairs whose legality verdict CP6 asserts against.
    // Illegal slots cannot round-trip through a loaded build (CheckAndFixAllEnhancements
    // strips them on load), so the port validates its reject against Mids' own
    // IsEnhancementValid verdict for each pair rather than a loaded build.
    private static readonly (string Power, string Enh)[] LegalityProbePairs =
    {
        // Resolved rejections (mids-port-spec § legality-predicates):
        // a generic Recharge IO is class-illegal in One with the Shield (its
        // Power.Enhancements has no Recharge class); Force Feedback (a Knockback set)
        // is set-type-illegal in Soul Drain (SetTypes has no Knockback).
        ("Scrapper_Defense.Shield_Defense.One_with_the_Shield", "Crafted_Recharge"),
        ("Scrapper_Melee.Dark_Melee.Soul_Drain", "Crafted_Force_Feedback_A"),
        // A control legal placement: a Recharge IO in Hasten (accepts Recharge).
        ("Pool.Speed.Hasten", "Crafted_Recharge"),
    };

    private static void DumpLegalityProbe(string outDir)
    {
        // Per named pair: Mids' IsEnhancementValid verdict plus the inputs the port's
        // legality port reads (Power.Enhancements / SetTypes, enh ClassIds / set type).
        var db = DatabaseAPI.Database;
        var probes = new List<object>();
        foreach (var (powerName, enhUid) in LegalityProbePairs)
        {
            var power = DatabaseAPI.GetPowerByFullName(powerName);
            var enhNid = DatabaseAPI.GetEnhancementByUIDName(enhUid);
            if (power == null || enhNid < 0)
            {
                Console.Error.WriteLine($"E20: legality-probe pair unresolved: power={powerName} enh={enhUid}");
                continue;
            }

            var enh = db.Enhancements[enhNid];
            probes.Add(new
            {
                PowerFullName = powerName,
                power.SetTypes,
                PowerEnhancements = power.Enhancements,
                EnhUid = enhUid,
                EnhNid = enhNid,
                EnhTypeName = enh.TypeID.ToString(),
                EnhNidSet = enh.nIDSet,
                // IsValid is the reference verdict the port's IsEnhancementValid port
                // must reproduce for each pair (two false, one true).
                IsValid = power.IsEnhancementValid(enhNid),
            });
        }
        WriteJson(outDir, "legality_probe.json", probes);
    }

    private static void DumpEnhancementEffects(string outDir)
    {
        // Per-enhancement effect data the value pipeline consumes: TypeID +
        // Superior gate the schedule multiplier; each Enhancement-mode sEffect
        // carries the aspect (Enhance.ID as eEnhance, SubID for Mez), the ED
        // schedule, the per-effect Multiplier, and the buff/debuff sign gate.
        // Only Mode==Enhancement effects contribute numeric aspects
        // (GetEnhancementEffect, I9Slot.cs:47), so FX/proc effects are dropped.
        // Keyed by the in-memory nID (the array index enhancements.json also
        // exposes), so the port matches this to a resolved slot's Enh.
        var db = DatabaseAPI.Database;
        var records = db.Enhancements
            .Select((e, nid) => (e, nid))
            .Where(t => t.e != null)
            .Select(t => new
            {
                Nid = t.nid,
                t.e.StaticIndex,
                TypeId = (int)t.e.TypeID,
                TypeName = t.e.TypeID.ToString(),
                t.e.Superior,
                t.e.nIDSet,
                Effects = t.e.Effect
                    .Where(fx => fx.Mode == Enums.eEffMode.Enhancement)
                    .Select(fx => new
                    {
                        Mode = fx.Mode.ToString(),
                        BuffMode = fx.BuffMode.ToString(),
                        EnhanceId = fx.Enhance.ID,
                        EnhanceName = ((Enums.eEnhance)fx.Enhance.ID).ToString(),
                        EnhanceSubId = fx.Enhance.SubID,
                        Schedule = (int)fx.Schedule,
                        ScheduleName = fx.Schedule.ToString(),
                        fx.Multiplier,
                    })
                    .ToList(),
            })
            .ToList();
        WriteJson(outDir, "enhancement_effects.json", records);
    }

    private static void DumpEnhancementSets(string outDir)
    {
        // Per enhancement SET (keyed by nID = array index): the tier + special
        // bonus definitions the port assembles the set-bonus virtual power from.
        // Bonus[] are the tiered (>=2 pieces) count bonuses; SpecialBonus[] are the
        // per-enhancement globals/uniques (>=1 piece), paired 1:1 with Enhancements[]
        // by index. Index[] values are global set_bonus Power ids (see
        // set_bonus_powers.json); Slotted is the 1-based piece threshold; PvMode
        // gates tier activation. The port never guesses these — it reads them here.
        var sets = DatabaseAPI.Database.EnhancementSets
            .Select((s, nid) => (s, nid))
            .Where(t => t.s != null)
            .Select(t => new
            {
                Nid = t.nid,
                t.s.Uid,
                t.s.DisplayName,
                t.s.SetType,
                // The eSetType name this set maps to; matched against a power's
                // SetTypes to decide whether the set is slottable in that power.
                SetTypeName = ((Enums.eSetType)t.s.SetType).ToString(),
                t.s.Enhancements,
                Bonus = t.s.Bonus.Select(b => new
                {
                    b.Slotted,
                    PvMode = (int)b.PvMode,
                    PvModeName = b.PvMode.ToString(),
                    b.Index,
                }).ToList(),
                SpecialBonus = t.s.SpecialBonus.Select(b => new
                {
                    b.Slotted,
                    PvMode = (int)b.PvMode,
                    b.Index,
                }).ToList(),
            })
            .ToList();
        WriteJson(outDir, "enhancement_sets.json", sets);
    }

    private static void DumpSetBonusPowers(string outDir)
    {
        // The bonus powers referenced by any EnhancementSet Bonus/SpecialBonus
        // Index[]: the exact key space the set-bonus virtual power clones effects
        // from and that the Rule-of-Five counter is keyed on (Mids' setCount is
        // sized to the whole Power array because NidPowers("set_bonus") does not
        // resolve a real powerset — it returns every id; only these referenced ids
        // are ever counted). Keyed by global Power id. MyPet* mirror
        // ShouldSkipEffects (Build.cs:1229-1234): a bonus whose Target AND
        // EntitiesAffected are both MyPet-flagged is excluded from the character's
        // own totals (but still consumes a Rule-of-Five slot).
        var db = DatabaseAPI.Database;
        var referenced = new SortedSet<int>();
        foreach (var set in db.EnhancementSets.Where(s => s != null))
        {
            foreach (var b in set.Bonus.Concat(set.SpecialBonus))
            {
                foreach (var id in b.Index.Where(id => id > -1))
                {
                    referenced.Add(id);
                }
            }
        }

        var powers = referenced
            .Where(id => id < db.Power.Length && db.Power[id] != null)
            .Select(id =>
            {
                var pw = db.Power[id];
                return new
                {
                    PowerId = id,
                    pw.FullName,
                    PowerType = pw.PowerType.ToString(),
                    MyPetTarget = pw.Target.HasFlag(Enums.eEntity.MyPet),
                    MyPetEntities = pw.EntitiesAffected.HasFlag(Enums.eEntity.MyPet),
                    Effects = pw.Effects.Select((fx, fxIdx) => SerializeEffect(fx, fxIdx)).ToList(),
                };
            })
            .ToList();
        WriteJson(outDir, "set_bonus_powers.json", powers);
    }

    private static void DumpBuildSetBonusVirtualPower(string buildDir, clsToonX toon)
    {
        // The GOLDEN for the port's assembled set-bonus virtual power. After
        // GenerateBuffedPowerArray, CurrentBuild.SetBonusVirtualPower holds the
        // cloned, Rule-of-Five-filtered bonus effects Mids folds into totals. The
        // port assembles its own virtual power from enhancement_sets + set_bonus_powers
        // and must reproduce these effects (structural key + Mag) before the fold.
        var vp = toon.CurrentBuild?.SetBonusVirtualPower;
        var effects = vp?.Effects.Select((fx, fxIdx) => SerializeVirtualEffect(fx, fxIdx)).ToList()
                      ?? new List<object>();
        WriteJson(buildDir, "set_bonus_virtual_power.json", new { EffectCount = effects.Count, Effects = effects });
    }

    private static void ExportMxdBuilds(string samplesDir, string outDir)
    {
        if (!Directory.Exists(samplesDir))
        {
            Console.Error.WriteLine($"E09: samples dir not found: {samplesDir}");
            return;
        }

        var mxdDir = Path.Combine(outDir, "mxd");
        Directory.CreateDirectory(mxdDir);

        // Recurse: samples/builds is split into community/ and operator-builds/ subfolders.
        foreach (var mbdPath in Directory.EnumerateFiles(samplesDir, "*.mbd", SearchOption.AllDirectories))
        {
            // A fresh character per build so an earlier load never bleeds into the next.
            MainModule.MidsController.Toon = new clsToonX();
            if (!BuildManager.Instance.LoadFromFile(mbdPath))
            {
                Console.Error.WriteLine($"E10: LoadFromFile failed for {mbdPath}");
                continue;
            }

            var mxd = MidsCharacterFileFormat.MxDBuildSaveString(true, false);
            if (string.IsNullOrEmpty(mxd))
            {
                Console.Error.WriteLine($"E11: MxDBuildSaveString returned empty for {mbdPath}");
                continue;
            }

            var outPath = Path.Combine(mxdDir, Path.GetFileNameWithoutExtension(mbdPath) + ".mxd");
            File.WriteAllText(outPath, mxd);
            Console.WriteLine($"exported {outPath}");
        }
    }

    private static void WriteJson(string outDir, string name, object payload)
    {
        var path = Path.Combine(outDir, name);
        File.WriteAllText(path, JsonSerializer.Serialize(payload, JsonOpts));
        Console.WriteLine($"wrote {path}");
    }

    private static void DumpVersion(string outDir)
    {
        WriteJson(outDir, "version.json", new
        {
            DatabaseVersion = DatabaseAPI.Database.Version.ToString(),
            DatabaseAPI.DatabaseName,
            DumpedAtUtc = DateTime.UtcNow.ToString("o"),
        });
    }

    private static void DumpServerData(string outDir)
    {
        var sd = DatabaseAPI.ServerData;
        WriteJson(outDir, "server_data.json", new
        {
            sd.BaseToHit,
            sd.MaxSlots,
            sd.EnableInherentSlotting,
            sd.BaseFlySpeed,
            sd.BaseJumpSpeed,
            sd.BaseJumpHeight,
            sd.BasePerception,
            sd.BaseRunSpeed,
            sd.MaxFlySpeed,
            sd.MaxJumpSpeed,
            sd.MaxJumpHeight,
            sd.MaxRunSpeed,
            sd.MaxMaxFlySpeed,
            sd.MaxMaxJumpSpeed,
            sd.MaxMaxRunSpeed,
        });
    }

    private static void DumpArchetypes(string outDir)
    {
        var ats = DatabaseAPI.Database.Classes.Select((at, idx) => new
        {
            Index = idx,
            at.ClassName,
            at.DisplayName,
            ClassType = at.ClassType.ToString(),
            at.Column,
            at.Playable,
            at.Hitpoints,
            at.HPCap,
            at.ResCap,
            at.DamageCap,
            at.RechargeCap,
            at.RecoveryCap,
            at.RegenCap,
            at.PerceptionCap,
            at.BaseRecovery,
            at.BaseRegen,
            at.BaseThreat,
        });
        WriteJson(outDir, "archetypes.json", ats.ToList());
    }

    private static void DumpMaths(string outDir)
    {
        var db = DatabaseAPI.Database;
        WriteJson(outDir, "maths.json", new
        {
            db.MultED,
            db.MultTO,
            db.MultDO,
            db.MultSO,
            db.MultHO,
            db.MultIO,
        });
    }

    private static void DumpEnhancementClasses(string outDir)
    {
        var classes = DatabaseAPI.Database.EnhancementClasses.Select(c => new
        {
            c.ID,
            c.ClassID,
            c.Name,
            c.ShortName,
            c.Desc,
        });
        WriteJson(outDir, "enhancement_classes.json", classes.ToList());
    }

    private static void DumpPowerIndex(string outDir)
    {
        // StaticIndex -> FullName map: the resolution layer .mxd build files need.
        var powers = DatabaseAPI.Database.Power
            .Where(p => p != null)
            .Select(p => new { p!.StaticIndex, p.FullName })
            .ToList();
        WriteJson(outDir, "power_static_index.json", powers);
    }
}
