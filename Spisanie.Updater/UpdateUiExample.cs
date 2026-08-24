using Spisanie.Updater;

namespace Spisanie.Updater.Integration;

/// <summary>
/// Пример вызова из главной формы программы Списание.
/// Скопируйте логику в свой код (кнопка «Проверить обновления» или старт приложения).
/// </summary>
public static class UpdateUiExample
{
    // Версия ТЕКУЩЕЙ сборки. Увеличивайте при каждом релизе вместе с versionCode на сервере.
    public const int AppVersionCode = 100;
    public const string AppVersion = "1.0.0";

    public static async Task CheckAndOfferUpdateAsync(
        Func<string, string, bool> askYesNo,
        Action<string> showInfo,
        Action<string> showError,
        CancellationToken ct = default)
    {
        try
        {
            var updater = new OtaUpdater(
                currentVersionCode: AppVersionCode,
                exeName: "Spisanie.exe");

            var check = await updater.CheckForUpdateAsync(ct).ConfigureAwait(true);
            if (!check.UpdateAvailable)
            {
                showInfo($"У вас актуальная версия {AppVersion}.");
                return;
            }

            var m = check.Manifest;
            var text =
                $"Доступна версия {m.Version}.\n\n" +
                $"{m.Changelog}\n\n" +
                (m.Mandatory ? "Обновление обязательное.\n\n" : "") +
                "Скачать и установить сейчас?";

            if (!m.Mandatory && !askYesNo("Обновление Списание", text))
                return;

            var progress = new Progress<UpdateProgress>(p =>
            {
                // Здесь можно обновить ProgressBar / статус в UI.
                showInfo(p.Message);
            });

            await updater.DownloadAndPrepareAsync(check.Manifest, progress, ct).ConfigureAwait(true);

            showInfo("Обновление скачано. Программа перезапустится.");
            updater.ApplyAndRestart();
            Environment.Exit(0);
        }
        catch (Exception ex)
        {
            showError("Не удалось обновить программу:\n" + ex.Message);
        }
    }
}
