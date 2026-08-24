using System.Text.Json.Serialization;

namespace Spisanie.Updater;

public sealed class UpdateManifest
{
    [JsonPropertyName("product")]
    public string Product { get; set; } = "Spisanie";

    [JsonPropertyName("version")]
    public string Version { get; set; } = "0.0.0";

    [JsonPropertyName("versionCode")]
    public int VersionCode { get; set; }

    [JsonPropertyName("minVersionCode")]
    public int MinVersionCode { get; set; }

    [JsonPropertyName("publishedAt")]
    public string? PublishedAt { get; set; }

    [JsonPropertyName("mandatory")]
    public bool Mandatory { get; set; }

    [JsonPropertyName("changelog")]
    public string? Changelog { get; set; }

    [JsonPropertyName("package")]
    public PackageInfo Package { get; set; } = new();

    [JsonPropertyName("exeName")]
    public string ExeName { get; set; } = "Spisanie.exe";

    [JsonPropertyName("channel")]
    public string Channel { get; set; } = "stable";
}

public sealed class PackageInfo
{
    [JsonPropertyName("url")]
    public string Url { get; set; } = "";

    [JsonPropertyName("fileName")]
    public string FileName { get; set; } = "";

    [JsonPropertyName("size")]
    public long Size { get; set; }

    [JsonPropertyName("sha256")]
    public string Sha256 { get; set; } = "";
}
