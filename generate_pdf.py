import os
import json
from fpdf import FPDF

# ---------- Paths ----------
book_folder = "English time 2"
# JSON files are now directly inside English time 2 (not in الاختبارات)
json_folder = book_folder
images_folder = os.path.join(book_folder, "images")
output_folder = os.path.join(book_folder, "output")
logo_path = "logo.png"

# Create output folder if it doesn't exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# ---------- Load all exams ----------
exams_data = []
for part in ["A", "B"]:
    for exam_num in range(1, 5):  # Exams 1 to 4
        filename = f"ET2_{part}_Exam{exam_num}.json"
        file_path = os.path.join(json_folder, filename)
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                exams_data.append(data)
        else:
            print(f"⚠️ Warning: {filename} not found in {json_folder}!")

# ---------- Generate PDFs ----------
for part in ["A", "B"]:
    # Filter exams for this part only
    part_exams = [exam for exam in exams_data if f"_{part}_" in exam["test_id"]]

    if not part_exams:
        print(f"No exams found for part {part}. Skipping.")
        continue

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    for exam in part_exams:
        pdf.add_page()

        # Add logo if exists
        if os.path.exists(logo_path):
            pdf.image(logo_path, x=10, y=8, w=30)
            pdf.ln(18)  # extra space after logo

        # Exam title
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, exam["title"], ln=True, align="C")
        pdf.ln(6)

        # Sections
        for section in exam["sections"]:
            # Section title
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, section["section_title"], ln=True)
            pdf.ln(2)

            # Section text (English, left-aligned)
            pdf.set_font("Arial", size=11)
            pdf.multi_cell(0, 7, section["text"])
            pdf.ln(3)

            # Images (if any)
            for img_info in section.get("images", []):
                img_name = img_info.get("suggested_filename", "")
                if not img_name:
                    continue
                img_path = os.path.join(images_folder, f"{img_name}.jpg")
                if os.path.exists(img_path):
                    try:
                        # Place image centered, width 140
                        pdf.image(img_path, x=35, y=None, w=140)
                        pdf.ln(4)
                    except Exception as e:
                        pdf.cell(0, 10, f"[Error loading image: {img_name}]", ln=True)
                else:
                    pdf.cell(0, 10, f"[Image missing: {img_name}]", ln=True)
            pdf.ln(4)

    # Save the combined PDF for this part
    output_file = os.path.join(output_folder, f"ET2_Basic_{part}_Exams.pdf")
    pdf.output(output_file)
    print(f"✅ Generated: {output_file}")

print("🎉 All exams have been printed successfully!")
