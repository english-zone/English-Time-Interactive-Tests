"""
ET2_generate_pdf.py
-------------------
يولّد ملفات PDF لامتحانات English Time 2
يستخدم reportlab بدل fpdf (دعم أفضل للخطوط والصور)
"""

import os
import json
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ─────────────────────────────────────────────
# 1. المسارات
# ─────────────────────────────────────────────
BOOK_FOLDER    = "English time 2"
JSON_FOLDER    = BOOK_FOLDER
IMAGES_FOLDER  = os.path.join(BOOK_FOLDER, "images")
OUTPUT_FOLDER  = os.path.join(BOOK_FOLDER, "output")
LOGO_PATH      = "logo.png"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ─────────────────────────────────────────────
# 2. الأنماط (Styles)
# ─────────────────────────────────────────────
styles = getSampleStyleSheet()

TITLE_STYLE = ParagraphStyle(
    "ExamTitle",
    parent=styles["Title"],
    fontSize=14,
    leading=18,
    textColor=colors.HexColor("#2c3e50"),
    spaceAfter=10,
    alignment=1,           # CENTER
)

SECTION_STYLE = ParagraphStyle(
    "SectionTitle",
    parent=styles["Heading2"],
    fontSize=12,
    leading=15,
    textColor=colors.HexColor("#007bff"),
    spaceBefore=8,
    spaceAfter=4,
    borderPad=4,
    borderColor=colors.HexColor("#007bff"),
    borderWidth=0,
    leftIndent=6,
    borderLeftWidth=3,     # خط جانبي أزرق
)

BODY_STYLE = ParagraphStyle(
    "Body",
    parent=styles["Normal"],
    fontSize=11,
    leading=16,
    spaceAfter=4,
    fontName="Helvetica",
)

MISSING_STYLE = ParagraphStyle(
    "Missing",
    parent=styles["Normal"],
    fontSize=9,
    textColor=colors.red,
    leading=12,
)

# ─────────────────────────────────────────────
# 3. تحميل ملفات JSON
# ─────────────────────────────────────────────
def load_exams():
    exams = []
    for part in ["A", "B"]:
        for num in range(1, 5):
            filename  = f"ET2_{part}_Exam{num}.json"
            filepath  = os.path.join(JSON_FOLDER, filename)
            if os.path.exists(filepath):
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # تأكد من وجود test_id
                    if "test_id" not in data:
                        data["test_id"] = f"ET2_{part}_Exam{num}"
                    exams.append(data)
                print(f"✅ Loaded: {filename}")
            else:
                print(f"⚠️  Not found: {filepath}")
    return exams

# ─────────────────────────────────────────────
# 4. بناء عناصر صفحة الامتحان
# ─────────────────────────────────────────────
def build_exam_story(exam):
    """يُعيد قائمة Flowables لامتحان واحد."""
    story = []

    # ── اللوجو ──────────────────────────────
    if os.path.exists(LOGO_PATH):
        logo = Image(LOGO_PATH, width=35*mm, height=35*mm, kind="proportional")
        logo.hAlign = "CENTER"
        story.append(logo)
        story.append(Spacer(1, 4*mm))

    # ── عنوان الامتحان ───────────────────────
    title = exam.get("title", exam.get("test_id", "Exam"))
    story.append(Paragraph(title, TITLE_STYLE))
    story.append(HRFlowable(width="100%", thickness=1,
                             color=colors.HexColor("#007bff"), spaceAfter=6))

    # ── الأقسام ──────────────────────────────
    for section in exam.get("sections", []):
        section_elements = []

        # عنوان القسم
        sec_title = section.get("section_title", "")
        section_elements.append(Paragraph(sec_title, SECTION_STYLE))

        # نص القسم — كل سطر فقرة مستقلة
        text = section.get("text", "")
        for line in text.split("\n"):
            line = line.strip()
            if line:
                # تجنب كسر XML داخل Paragraph
                safe = (line.replace("&", "&amp;")
                            .replace("<", "&lt;")
                            .replace(">", "&gt;"))
                section_elements.append(Paragraph(safe, BODY_STYLE))

        # الصور
        for img_info in section.get("images", []):
            img_name = img_info.get("suggested_filename", "")
            if not img_name:
                continue

            # جرّب jpg ثم png
            img_path = None
            for ext in [".jpg", ".jpeg", ".png", ".gif"]:
                candidate = os.path.join(IMAGES_FOLDER, f"{img_name}{ext}")
                if os.path.exists(candidate):
                    img_path = candidate
                    break

            if img_path:
                try:
                    img = Image(img_path, width=120*mm, height=60*mm,
                                kind="proportional")
                    img.hAlign = "CENTER"
                    section_elements.append(Spacer(1, 3*mm))
                    section_elements.append(img)
                    section_elements.append(Spacer(1, 3*mm))
                except Exception as e:
                    section_elements.append(
                        Paragraph(f"[خطأ في تحميل الصورة: {img_name}] — {e}",
                                  MISSING_STYLE))
            else:
                section_elements.append(
                    Paragraph(f"[صورة غير موجودة: {img_name}]", MISSING_STYLE))

        # ابقِ عنوان القسم مع أول سطرين معه
        story.append(KeepTogether(section_elements[:3]))
        story.extend(section_elements[3:])
        story.append(Spacer(1, 5*mm))

    return story

# ─────────────────────────────────────────────
# 5. توليد PDF لكل جزء
# ─────────────────────────────────────────────
def generate_pdfs(exams):
    for part in ["A", "B"]:
        part_exams = [e for e in exams
                      if f"_{part}_" in e.get("test_id", "")]

        if not part_exams:
            print(f"⚠️  لا توجد امتحانات للجزء {part}. تخطّي.")
            continue

        output_file = os.path.join(OUTPUT_FOLDER, f"ET2_Basic_{part}_Exams.pdf")

        doc = SimpleDocTemplate(
            output_file,
            pagesize=A4,
            leftMargin=15*mm,
            rightMargin=15*mm,
            topMargin=15*mm,
            bottomMargin=20*mm,
        )

        full_story = []
        for i, exam in enumerate(part_exams):
            full_story.extend(build_exam_story(exam))
            if i < len(part_exams) - 1:
                full_story.append(PageBreak())

        doc.build(full_story)
        print(f"✅ Generated: {output_file}")

# ─────────────────────────────────────────────
# 6. التنفيذ
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 50)
    print("  English Time 2 — PDF Generator")
    print("=" * 50)

    exams = load_exams()

    if not exams:
        print("❌ لم يُعثر على أي ملفات JSON. تأكد من المسارات.")
    else:
        print(f"\n📚 تم تحميل {len(exams)} امتحان. جاري التوليد...\n")
        generate_pdfs(exams)
        print("\n🎉 اكتمل توليد جميع ملفات PDF!")
