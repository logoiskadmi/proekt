# OTA-обновления программы «Списание»

Программа на клиенте сама проверяет сервер и ставит новую версию.

## Адрес на сервере

```
https://lognet.by/ota/Spisanie/version.json
https://lognet.by/ota/Spisanie/Spisanie-X.Y.Z.zip
```

Файлы кладите в:

```
www/lognet.by/ota/Spisanie/
```

## Как это работает

1. Приложение спрашивает `version.json`.
2. Если `versionCode` на сервере больше локального — предлагает обновиться.
3. Скачивает ZIP, проверяет SHA-256.
4. После выхода из программы копирует файлы и запускает `Spisanie.exe` снова.

## Что загрузить на сервер

| Файл | Назначение |
|------|------------|
| `version.json` | Манифест текущей версии |
| `Spisanie-1.0.1.zip` | Архив сборки (exe + dll + нужные файлы) |
| `.htaccess` | Для Apache (уже в репо) |

Если сайт на **nginx + Next.js**, добавьте фрагмент из `nginx-snippet.conf`, иначе вместо JSON может отдаваться HTML главной страницы.

Сейчас `/ota/Spisanie/` отвечает **403** (листинг закрыт — это нормально). Файл `version.json` должен отдаваться как **application/json**.

## Публикация новой версии (Windows)

```powershell
.\scripts\publish-ota.ps1 `
  -SourceDir "D:\path\to\Spisanie\Release" `
  -Version "1.0.1" `
  -VersionCode 101 `
  -Changelog "Уменьшен размер, исправления списания"
```

Скрипт создаст ZIP + `version.json` с правильным `sha256`.  
Затем скопируйте оба файла в `www/lognet.by/ota/Spisanie/`.

## Встраивание в программу

1. Добавьте проект `Spisanie.Updater` в решение (или скопируйте файлы `.cs`).
2. В приложении задайте текущий `versionCode` (например `100` для `1.0.0`).
3. На старте или по кнопке «Проверить обновления» вызовите логику из `UpdateUiExample.cs`.

Минимальный вызов:

```csharp
var updater = new OtaUpdater(currentVersionCode: 100, exeName: "Spisanie.exe");
var check = await updater.CheckForUpdateAsync();
if (check.UpdateAvailable)
{
    await updater.DownloadAndPrepareAsync(check.Manifest);
    updater.ApplyAndRestart();
    Environment.Exit(0);
}
```

## Важно

- В ZIP кладите **содержимое** папки программы, не саму папку-обёртку.
- Имя exe в манифесте (`exeName`) должно совпадать с реальным.
- Базу данных (`*.db`, `*.mdb`, данные пользователей) лучше хранить **вне** папки обновляемых файлов или исключать из ZIP, чтобы не затереть.
- После каждой публикации увеличивайте и `version`, и `versionCode` в коде приложения.

## Проверка после загрузки

```bash
curl -sI https://lognet.by/ota/Spisanie/version.json
curl -s  https://lognet.by/ota/Spisanie/version.json
```

Ожидается JSON, не HTML-страница LogNet.
