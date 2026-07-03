// OracleDump — test-only harness that loads the MidsReborn Homecoming database
// headless (no UI) and dumps the data the Python port (src/coh_engine) baselines
// its golden fixtures against.
//
// Usage: OracleDump <databases-dir> <output-dir>
//   <databases-dir>  e.g. <midsreborn-fork>/MidsReborn/Databases/Homecoming
//   <output-dir>     directory to write the JSON dumps into (created if missing)
//
// Load sequence mirrors MainModule.LoadDataAsync (MidsReborn MainModule.cs:145-218),
// minus graphics. Dialogs only fire on load errors.

using System.Text.Json;
using System.Text.Json.Serialization;
using Mids_Reborn.Core;
using Mids_Reborn.Core.Base.Master_Classes;

namespace OracleDump;

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
            Console.Error.WriteLine("usage: OracleDump <databases-dir> <output-dir>");
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
        DumpPowerIndex(outDir);

        Console.WriteLine($"OK: dumps written to {outDir}");
        return 0;
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
