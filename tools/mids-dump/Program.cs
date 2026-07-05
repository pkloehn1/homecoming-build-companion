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

        DumpVersion(outDir);
        DumpServerData(outDir);
        DumpArchetypes(outDir);
        DumpMaths(outDir);
        DumpEnhancementClasses(outDir);
        DumpEnhancements(outDir);
        DumpEnhancementEffects(outDir);
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

            var buildDir = Path.Combine(outDir, "builds", Path.GetFileNameWithoutExtension(mbdPath));
            Directory.CreateDirectory(buildDir);
            DumpBuildPowersEffects(buildDir, toon);
            DumpBuildSlots(buildDir, toon);
            DumpBuildEnhancedPowers(buildDir, toon);
            DumpBuildTotals(buildDir, toon);
        }

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
                pw.Level,
                pw.EndCost,
                pw.ActivatePeriod,
                pw.ToggleCost,
                pw.VariableEnabled,
                entry.StatInclude,
                entry.VariableValue,
                Effects = pw.Effects.Select((fx, fxIdx) => new
                {
                    Index = fxIdx,
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
                }).ToList(),
            });
        }
        WriteJson(buildDir, "powers_effects.json", powers);
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
                    EffectType = fx.EffectType.ToString(),
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
        var db = DatabaseAPI.Database;
        var enhancements = db.Enhancements
            .Select((e, nid) => (e, nid))
            .Where(t => t.e != null)
            .Select(t => new
            {
                Nid = t.nid,
                t.e.StaticIndex,
                t.e.UID,
                TypeId = (int)t.e.TypeID,
                TypeName = t.e.TypeID.ToString(),
            })
            .ToList();
        WriteJson(outDir, "enhancements.json", enhancements);
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
