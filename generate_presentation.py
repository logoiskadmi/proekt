from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


ROOT = Path(__file__).parent
OUT_DIR = ROOT / "assets" / "presentation"
OUT_DIR.mkdir(parents=True, exist_ok=True)
PDF_PATH = ROOT / "DOMA_CTRL_presentation.pdf"


def load_font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size)


def make_gradient_image(path: Path, c1, c2):
    w, h = 1600, 900
    img = Image.new("RGB", (w, h), c1)
    draw = ImageDraw.Draw(img)
    for y in range(h):
        t = y / h
        color = tuple(int(c1[i] * (1 - t) + c2[i] * t) for i in range(3))
        draw.line([(0, y), (w, y)], fill=color)
    img.save(path)


def draw_controller_panel(path: Path):
    make_gradient_image(path, (22, 38, 62), (13, 19, 34))
    img = Image.open(path)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((180, 120, 1420, 780), radius=28, outline=(180, 205, 235), width=5)
    d.rectangle((230, 180, 1370, 260), fill=(70, 90, 120))
    d.text((260, 205), "DOMA CTRL / DIN Controller", fill=(240, 245, 255), font=load_font(38))
    for i in range(8):
        x = 260 + i * 130
        d.rounded_rectangle((x, 330, x + 95, 520), radius=12, fill=(210, 220, 235))
        d.rectangle((x + 22, 355, x + 72, 505), fill=(120, 145, 180))
    for i in range(10):
        y = 600 + i * 14
        d.line([(240, y), (1360, y)], fill=(90, 120, 170), width=4)
    d.ellipse((1260, 180, 1320, 240), fill=(38, 224, 127))
    d.text((1120, 192), "Online", fill=(230, 255, 240), font=load_font(30))
    img.save(path)


def draw_mobile_desktop(path: Path):
    make_gradient_image(path, (16, 60, 90), (21, 88, 136))
    img = Image.open(path)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((180, 120, 910, 730), radius=26, fill=(235, 244, 255))
    d.rectangle((220, 180, 870, 670), fill=(255, 255, 255))
    d.rectangle((240, 210, 840, 260), fill=(224, 235, 250))
    d.text((265, 222), "Dashboard", fill=(27, 50, 80), font=load_font(34))
    labels = ["Light", "Heating", "Leak", "Away"]
    for i, label in enumerate(labels):
        y = 300 + i * 85
        d.rounded_rectangle((260, y, 820, y + 60), radius=16, fill=(236, 245, 255))
        d.text((290, y + 14), label, fill=(40, 65, 98), font=load_font(30))
        color = (48, 195, 124) if i % 2 == 0 else (162, 173, 190)
        d.rounded_rectangle((730, y + 14, 790, y + 46), radius=14, fill=color)
    d.rounded_rectangle((1020, 170, 1300, 730), radius=36, fill=(28, 38, 58))
    d.rounded_rectangle((1048, 220, 1272, 690), radius=22, fill=(249, 252, 255))
    d.text((1075, 255), "Home", fill=(32, 56, 86), font=load_font(34))
    d.ellipse((1088, 340, 1146, 398), fill=(58, 195, 124))
    d.text((1170, 352), "All safe", fill=(29, 66, 96), font=load_font(28))
    d.ellipse((1088, 440, 1146, 498), fill=(255, 182, 75))
    d.text((1170, 452), "18:00 scene", fill=(29, 66, 96), font=load_font(28))
    img.save(path)


def draw_house_automation(path: Path):
    make_gradient_image(path, (35, 45, 75), (69, 94, 148))
    img = Image.open(path)
    d = ImageDraw.Draw(img)
    d.polygon([(180, 360), (800, 120), (1420, 360), (1420, 760), (180, 760)], fill=(238, 244, 252))
    d.polygon([(180, 360), (800, 120), (1420, 360)], fill=(168, 184, 212))
    rooms = [
        ((240, 420, 610, 720), "Kitchen", (255, 210, 95)),
        ((650, 420, 980, 720), "Living", (114, 194, 255)),
        ((1020, 420, 1360, 720), "Bedroom", (165, 231, 178)),
    ]
    for box, name, color in rooms:
        d.rounded_rectangle(box, radius=14, fill=color)
        d.text((box[0] + 20, box[1] + 20), name, fill=(40, 50, 70), font=load_font(34))
    d.rounded_rectangle((690, 260, 910, 360), radius=20, fill=(34, 58, 92))
    d.text((730, 292), "Controller", fill=(235, 245, 255), font=load_font(30))
    centers = [(425, 510), (815, 510), (1190, 510)]
    for cx, cy in centers:
        d.line([(800, 360), (cx, cy)], fill=(61, 132, 255), width=6)
        d.ellipse((cx - 20, cy - 20, cx + 20, cy + 20), fill=(43, 110, 220))
    img.save(path)


def draw_installer_partner(path: Path):
    make_gradient_image(path, (55, 72, 95), (100, 128, 165))
    img = Image.open(path)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((170, 120, 760, 760), radius=30, fill=(230, 237, 248))
    d.rectangle((230, 190, 700, 690), outline=(70, 95, 130), width=5)
    for i in range(6):
        y = 240 + i * 68
        d.line([(260, y), (670, y)], fill=(110, 135, 170), width=5)
    d.ellipse((900, 230, 1100, 430), fill=(245, 204, 167))
    d.rounded_rectangle((860, 420, 1140, 740), radius=30, fill=(52, 88, 130))
    d.ellipse((1170, 250, 1370, 450), fill=(246, 215, 182))
    d.rounded_rectangle((1130, 440, 1410, 740), radius=30, fill=(105, 132, 171))
    d.line([(1000, 500), (1240, 530)], fill=(255, 255, 255), width=8)
    d.text((865, 780), "Installer + Homeowner", fill=(240, 246, 255), font=load_font(42))
    img.save(path)


def draw_growth(path: Path):
    make_gradient_image(path, (16, 31, 54), (29, 62, 108))
    img = Image.open(path)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((120, 140, 1480, 760), radius=30, outline=(150, 192, 255), width=4)
    points = [(200, 700), (420, 620), (620, 590), (830, 500), (1080, 420), (1370, 260)]
    for p1, p2 in zip(points[:-1], points[1:]):
        d.line([p1, p2], fill=(64, 214, 136), width=12)
    for x, y in points:
        d.ellipse((x - 16, y - 16, x + 16, y + 16), fill=(255, 211, 99))
    d.rounded_rectangle((210, 250, 560, 460), radius=22, fill=(42, 80, 126))
    d.text((250, 300), "Pilot", fill=(235, 245, 255), font=load_font(46))
    d.rounded_rectangle((660, 250, 1030, 460), radius=22, fill=(42, 80, 126))
    d.text((700, 300), "Sales", fill=(235, 245, 255), font=load_font(46))
    d.rounded_rectangle((1120, 250, 1390, 460), radius=22, fill=(42, 80, 126))
    d.text((1155, 300), "Scale", fill=(235, 245, 255), font=load_font(46))
    img.save(path)


def register_font():
    pdfmetrics.registerFont(TTFont("DejaVuSans", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
    pdfmetrics.registerFont(TTFont("DejaVuSansBold", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))


def bullet_lines(c: canvas.Canvas, x: int, y: int, lines):
    c.setFont("DejaVuSans", 24)
    step = 42
    for idx, line in enumerate(lines):
        c.drawString(x, y - idx * step, f"• {line}")


def build_pdf(images: dict[str, Path]):
    width, height = 1366, 768
    c = canvas.Canvas(str(PDF_PATH), pagesize=(width, height))

    slides = [
        {
            "title": "DOMA CTRL",
            "subtitle": "Умный дом, который настраивает обычный пользователь",
            "bullets": [
                "Контроллер для электрощита + интуитивное ПО",
                "Настройка с телефона или компьютера за 20 минут",
                "Локальная работа и безопасная автоматизация",
            ],
            "image": images["controller"],
        },
        {
            "title": "Проблема рынка",
            "subtitle": "Сложность и зависимость от интеграторов",
            "bullets": [
                "Текущие системы требуют специалиста на каждом шаге",
                "Пользователь боится сложной настройки и рисков",
                "Облачные решения нестабильны при потере интернета",
            ],
            "image": images["mobile"],
        },
        {
            "title": "Наше решение",
            "subtitle": "Единая платформа: DIN-контроллер + понятный интерфейс",
            "bullets": [
                "Wizard первого запуска без технического жаргона",
                "Шаблоны: квартира, дом, дача",
                "Базовые сценарии света, отопления и безопасности",
            ],
            "image": images["house"],
        },
        {
            "title": "Как это работает",
            "subtitle": "Путь клиента от коробки до запуска",
            "bullets": [
                "Установка в щит и скан QR-кода",
                "Назначение линий: кухня, насос, теплый пол",
                "Проверка линий и запуск сценариев одним нажатием",
            ],
            "image": images["controller"],
        },
        {
            "title": "Продукт MVP",
            "subtitle": "Функциональность первой коммерческой версии",
            "bullets": [
                "6–8 входов / 6–8 выходов, Ethernet + Wi‑Fi + BLE",
                "Локальный веб-интерфейс и мобильный PWA",
                "Резервная копия конфигурации и журнал событий",
            ],
            "image": images["mobile"],
        },
        {
            "title": "Целевая аудитория в РБ",
            "subtitle": "B2C + партнерская модель с инсталляторами",
            "bullets": [
                "Квартиры в новостройках и частные дома",
                "Электромонтажники как канал продаж и внедрения",
                "Небольшие коммерческие объекты: офисы, студии, салоны",
            ],
            "image": images["partner"],
        },
        {
            "title": "Конкурентные преимущества",
            "subtitle": "Проще внедрить, легче масштабировать",
            "bullets": [
                "Настройка без программиста и интегратора",
                "Работает локально без критической зависимости от облака",
                "Расширяется через RS‑485/Modbus",
            ],
            "image": images["house"],
        },
        {
            "title": "Go-to-market",
            "subtitle": "План вывода продукта на рынок Беларуси",
            "bullets": [
                "Пилот 10–20 объектов с партнерами-электриками",
                "Лендинг и видео-демо «запуск за 20 минут»",
                "Подготовка документации и соответствия ЕАЭС/EAC",
            ],
            "image": images["partner"],
        },
        {
            "title": "Финансовая модель",
            "subtitle": "Доход от железа, услуг и подписки",
            "bullets": [
                "Линейка: Starter / Home / Pro",
                "Доп. выручка: установка и сервисное обслуживание",
                "Опциональная подписка: мониторинг и бэкапы",
            ],
            "image": images["growth"],
        },
        {
            "title": "Дорожная карта",
            "subtitle": "MVP → пилот → продажи → масштабирование",
            "bullets": [
                "Q1: железо MVP и базовое ПО",
                "Q2: пилоты и доработка UX по обратной связи",
                "Q3: сертификация и коммерческий запуск в РБ",
            ],
            "image": images["growth"],
        },
    ]

    for slide in slides:
        c.setFillColorRGB(0.06, 0.12, 0.24)
        c.rect(0, 0, width, height, stroke=0, fill=1)
        c.setFillColorRGB(1, 1, 1)
        c.setFont("DejaVuSansBold", 44)
        c.drawString(56, 682, slide["title"])
        c.setFont("DejaVuSans", 24)
        c.setFillColorRGB(0.82, 0.89, 1)
        c.drawString(56, 640, slide["subtitle"])
        bullet_lines(c, 62, 566, slide["bullets"])

        img = ImageReader(str(slide["image"]))
        c.drawImage(img, 700, 108, width=620, height=540, preserveAspectRatio=True, mask="auto")
        c.setFillColorRGB(1, 1, 1)
        c.setFont("DejaVuSans", 14)
        c.drawString(56, 40, "DOMA CTRL • Презентация продукта • 2026")
        c.showPage()

    c.save()


def main():
    controller = OUT_DIR / "01_controller.png"
    mobile = OUT_DIR / "02_mobile_ui.png"
    house = OUT_DIR / "03_house.png"
    partner = OUT_DIR / "04_partner.png"
    growth = OUT_DIR / "05_growth.png"

    draw_controller_panel(controller)
    draw_mobile_desktop(mobile)
    draw_house_automation(house)
    draw_installer_partner(partner)
    draw_growth(growth)
    register_font()
    build_pdf(
        {
            "controller": controller,
            "mobile": mobile,
            "house": house,
            "partner": partner,
            "growth": growth,
        }
    )
    print(f"Created: {PDF_PATH}")


if __name__ == "__main__":
    main()
