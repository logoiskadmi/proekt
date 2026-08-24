using System.Diagnostics;
using System.IO.Compression;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;

namespace Spisanie.Updater;

/// <summary>
/// Клиент OTA: проверяет https://lognet.by/ota/Spisanie/version.json,
/// скачивает ZIP, проверяет SHA-256 и устанавливает обновление.
/// </summary>
public sealed class OtaUpdater
{
    public const string DefaultManifestUrl = "https://lognet.by/ota/Spisanie/version.json";

    private static readonly JsonSerializerOptions JsonOptions = new()
    {
        PropertyNameCaseInsensitive = true
    };

    private readonly HttpClient _http;
    private readonly string _manifestUrl;
    private readonly int _currentVersionCode;
    private readonly string _installDir;
    private readonly string _exeName;

    public OtaUpdater(
        int currentVersionCode,
        string? installDir = null,
        string exeName = "Spisanie.exe",
        string? manifestUrl = null,
        HttpClient? httpClient = null)
    {
        _currentVersionCode = currentVersionCode;
        _installDir = installDir ?? AppContext.BaseDirectory.TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar);
        _exeName = exeName;
        _manifestUrl = manifestUrl ?? DefaultManifestUrl;
        _http = httpClient ?? new HttpClient { Timeout = TimeSpan.FromMinutes(10) };
    }

    public async Task<UpdateCheckResult> CheckForUpdateAsync(CancellationToken ct = default)
    {
        using var response = await _http.GetAsync(_manifestUrl, HttpCompletionOption.ResponseHeadersRead, ct).ConfigureAwait(false);
        response.EnsureSuccessStatusCode();

        var mediaType = response.Content.Headers.ContentType?.MediaType ?? "";
        var body = await response.Content.ReadAsStringAsync(ct).ConfigureAwait(false);

        if (mediaType.Contains("html", StringComparison.OrdinalIgnoreCase) ||
            body.TrimStart().StartsWith("<!", StringComparison.Ordinal))
        {
            throw new InvalidOperationException(
                "Сервер вернул HTML вместо version.json. " +
                "Загрузите файл на https://lognet.by/ota/Spisanie/version.json " +
                "и настройте nginx (см. ota/Spisanie/nginx-snippet.conf).");
        }

        var manifest = JsonSerializer.Deserialize<UpdateManifest>(body, JsonOptions)
            ?? throw new InvalidOperationException("Не удалось разобрать version.json.");

        var available = manifest.VersionCode > _currentVersionCode;
        return new UpdateCheckResult(available, manifest, _currentVersionCode);
    }

    public async Task DownloadAndPrepareAsync(
        UpdateManifest manifest,
        IProgress<UpdateProgress>? progress = null,
        CancellationToken ct = default)
    {
        if (string.IsNullOrWhiteSpace(manifest.Package.Url))
            throw new InvalidOperationException("В манифесте нет URL пакета.");

        if (string.IsNullOrWhiteSpace(manifest.Package.Sha256) ||
            manifest.Package.Sha256.StartsWith("REPLACE_", StringComparison.OrdinalIgnoreCase))
            throw new InvalidOperationException("В манифесте не указан корректный sha256 пакета.");

        var staging = Path.Combine(Path.GetTempPath(), "SpisanieOTA", manifest.Version);
        Directory.CreateDirectory(staging);

        var zipPath = Path.Combine(staging, string.IsNullOrWhiteSpace(manifest.Package.FileName)
            ? $"Spisanie-{manifest.Version}.zip"
            : manifest.Package.FileName);

        progress?.Report(new UpdateProgress(UpdateStage.Downloading, 0, "Скачивание обновления…"));
        await DownloadFileAsync(manifest.Package.Url, zipPath, progress, ct).ConfigureAwait(false);

        progress?.Report(new UpdateProgress(UpdateStage.Verifying, 100, "Проверка контрольной суммы…"));
        var actualHash = await ComputeSha256Async(zipPath, ct).ConfigureAwait(false);
        if (!actualHash.Equals(manifest.Package.Sha256.Trim(), StringComparison.OrdinalIgnoreCase))
        {
            File.Delete(zipPath);
            throw new InvalidOperationException(
                $"SHA-256 не совпал.\nОжидался: {manifest.Package.Sha256}\nПолучен: {actualHash}");
        }

        var extractDir = Path.Combine(staging, "payload");
        if (Directory.Exists(extractDir))
            Directory.Delete(extractDir, recursive: true);
        Directory.CreateDirectory(extractDir);

        progress?.Report(new UpdateProgress(UpdateStage.Extracting, 100, "Распаковка…"));
        ZipFile.ExtractToDirectory(zipPath, extractDir, overwriteFiles: true);

        var helperPath = Path.Combine(staging, "apply-update.cmd");
        File.WriteAllText(helperPath, BuildApplyScript(extractDir, _installDir, _exeName), Encoding.Default);

        progress?.Report(new UpdateProgress(UpdateStage.Ready, 100, "Готово к установке"));
        PreparedHelperPath = helperPath;
        PreparedExtractDir = extractDir;
    }

    /// <summary>Путь к .cmd, который заменит файлы после выхода из программы.</summary>
    public string? PreparedHelperPath { get; private set; }

    public string? PreparedExtractDir { get; private set; }

    /// <summary>
    /// Запускает helper и завершает текущий процесс.
    /// Вызывайте после закрытия БД/файлов приложения.
    /// </summary>
    public void ApplyAndRestart()
    {
        if (string.IsNullOrWhiteSpace(PreparedHelperPath) || !File.Exists(PreparedHelperPath))
            throw new InvalidOperationException("Сначала вызовите DownloadAndPrepareAsync.");

        var psi = new ProcessStartInfo
        {
            FileName = "cmd.exe",
            Arguments = $"/c \"{PreparedHelperPath}\"",
            UseShellExecute = true,
            WindowStyle = ProcessWindowStyle.Hidden,
            WorkingDirectory = Path.GetDirectoryName(PreparedHelperPath)!
        };
        Process.Start(psi);
    }

    private async Task DownloadFileAsync(
        string url,
        string destination,
        IProgress<UpdateProgress>? progress,
        CancellationToken ct)
    {
        using var response = await _http.GetAsync(url, HttpCompletionOption.ResponseHeadersRead, ct).ConfigureAwait(false);
        response.EnsureSuccessStatusCode();

        var total = response.Content.Headers.ContentLength ?? -1L;
        await using var source = await response.Content.ReadAsStreamAsync(ct).ConfigureAwait(false);
        await using var target = new FileStream(destination, FileMode.Create, FileAccess.Write, FileShare.None, 81920, useAsync: true);

        var buffer = new byte[81920];
        long readTotal = 0;
        int read;
        while ((read = await source.ReadAsync(buffer.AsMemory(0, buffer.Length), ct).ConfigureAwait(false)) > 0)
        {
            await target.WriteAsync(buffer.AsMemory(0, read), ct).ConfigureAwait(false);
            readTotal += read;
            if (total > 0)
            {
                var pct = (int)(readTotal * 100 / total);
                progress?.Report(new UpdateProgress(UpdateStage.Downloading, pct, $"Скачивание… {pct}%"));
            }
        }
    }

    private static async Task<string> ComputeSha256Async(string path, CancellationToken ct)
    {
        await using var stream = File.OpenRead(path);
        var hash = await SHA256.HashDataAsync(stream, ct).ConfigureAwait(false);
        return Convert.ToHexString(hash).ToLowerInvariant();
    }

    private static string BuildApplyScript(string extractDir, string installDir, string exeName)
    {
        // Ждём завершения Spisanie.exe, копируем файлы, запускаем снова.
        return $"""
            @echo off
            setlocal
            set "SRC={extractDir}"
            set "DST={installDir}"
            set "EXE={exeName}"
            :wait
            tasklist /FI "IMAGENAME eq %EXE%" 2>NUL | find /I "%EXE%" >NUL
            if not errorlevel 1 (
              timeout /t 1 /nobreak >NUL
              goto wait
            )
            timeout /t 1 /nobreak >NUL
            xcopy "%SRC%\*" "%DST%\" /E /Y /I /Q >NUL
            start "" "%DST%\%EXE%"
            endlocal
            """;
    }
}

public sealed record UpdateCheckResult(bool UpdateAvailable, UpdateManifest Manifest, int CurrentVersionCode);

public enum UpdateStage
{
    Downloading,
    Verifying,
    Extracting,
    Ready
}

public sealed record UpdateProgress(UpdateStage Stage, int Percent, string Message);
