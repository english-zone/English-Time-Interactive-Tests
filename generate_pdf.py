import os
import json
from fpdf import FPDF

# المسارات الثابتة
book_folder = "English time 2"
tests_folder = os.path.join(book_folder, "الاختبارات")
images_folder = os.path.join(book_folder, "images")
output_folder = os.path.join(book_folder, "output")
logo_path = "logo.png"

# التأكد من وجود مجلد الإخراج
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# تجميع الاختبارات
exams_data = []

# قراءة ملفات الـ 8 اختبارات
for part in ["A", "B"]:
    for exam_num in range(1, 5):  # من 1 إلى 4
        filename = f"ET2_{part}_Exam{exam_num}.json"
        file_path = os.path.join(tests_folder, filename)
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                exams_data.append(data)
        else:
            print(f"⚠️ تحذير: ملف {filename} غير موجود في مجلد الاختبارات!")

# توليد ملفات PDF
for part in ["A", "B"]:
    # تصفية الاختبارات لهذا الجزء فقط
    part_exams = [exam for exam in exams_data if f"_{part}_" in exam['test_id']]
    
    if not part_exams:
        continue

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    for exam in part_exams:
        pdf.add_page()
        
        # إضافة الشعار للصفحة الأولى (أو لكل صفحة)
        if os.path.exists(logo_path):
            pdf.image(logo_path, x=10, y=8, w=30)
            pdf.ln(15)
        
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, f"{exam['title']}", ln=True, align='C')
        pdf.ln(5)

        pdf.set_font("Arial", size=12)

        for section in exam['sections']:
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, section['section_title'], ln=True)
            pdf.set_font("Arial", size=12)
            pdf.ln(3)
            
            # طباعة النص
            pdf.multi_cell(0, 8, section['text'])
            pdf.ln(3)
            
            # طباعة الصور (إذا كانت موجودة في مجلد images)
            for img_info in section['images']:
                # محاولة البحث بصيغة jpg (يمكنك إضافة png إذا أردت)
                img_name = img_info['suggested_filename']
                img_path = os.path.join(images_folder, f"{img_name}.jpg")
                
                if os.path.exists(img_path):
                    try:
                        pdf.image(img_path, x=30, y=None, w=140)
                        pdf.ln(5)
                    except:
                        pass
                else:
                    pdf.cell(0, 10, f"[صورة '{img_name}' غير موجودة]", ln=True)
            pdf.ln(5)
    
    # حفظ ملف الـ PDF الناتج
    output_file = os.path.join(output_folder, f"ET2_Basic_{part}_Exams.pdf")
    pdf.output(output_file)
    print(f"✅ تم توليد ملف: {output_file}")

print("🎉 اكتملت طباعة اختبارات English Time 2 بنجاح!")
