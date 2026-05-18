
import os
import requests
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

# Font URLs
font_regular_url = "https://raw.githubusercontent.com/google/fonts/main/ofl/amiri/Amiri-Regular.ttf"
font_bold_url = "https://raw.githubusercontent.com/google/fonts/main/ofl/amiri/Amiri-Bold.ttf"

font_regular_path = "Amiri-Regular.ttf"
font_bold_path = "Amiri-Bold.ttf"


def download_font(url, path):
    if os.path.exists(path):
        print(f"{path} already exists.")
        return

    print(f"Downloading {path} ...")
    r = requests.get(url)

    if r.status_code != 200:
        raise Exception("Failed to download font")

    with open(path, "wb") as f:
        f.write(r.content)

    print("Done!")


def register_fonts():
    download_font(font_regular_url, font_regular_path)
    download_font(font_bold_url, font_bold_path)

    pdfmetrics.registerFont(TTFont("Arabic", font_regular_path))
    pdfmetrics.registerFont(TTFont("Arabic-Bold", font_bold_path))

    print("Arabic fonts registered successfully!")
