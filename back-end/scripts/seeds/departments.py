import uuid
from app.models import Department

def get_department_seeds(faculty_map):
    # Mapping specifically to "No Faculty" (Order 0)
    no_faculty_id = faculty_map["No Faculty"]

    return [
        # --- Departments under "No Faculty" ---
        Department(
            name_bangla="Default", alias_bangla="Default", 
            faculty_id=faculty_map["Default"]
        ),
        Department(
            name_bangla="মানবিক বিভাগ", name_english="Dept of Humanities",
            alias_bangla="মানবিক", alias_english="HUM",
            faculty_id=no_faculty_id
        ),
        Department(
            name_bangla="নগর ও অঞ্চল পরিকল্পনা বিভাগ", name_english="Dept of Urban & Regional Planning",
            alias_bangla="ইউআরপি", alias_english="URP",
            faculty_id=no_faculty_id
        ),
        Department(
            name_bangla="ইনস্টিটিউট অব ওয়াটার এন্ড ফ্লাড ম্যানেজমেন্ট", name_english="IWFM",
            alias_bangla="আইডব্লিউএফএম", alias_english="IWFM",
            faculty_id=no_faculty_id
        ),
        Department(
            name_bangla="ইনস্টিটিউট অব ইনফরমেশন এন্ড কমিউনিকেশন টেকনোলজি", name_english="IICT",
            alias_bangla="আইআইসিটি", alias_english="IICT",
            faculty_id=no_faculty_id
        ),
        Department(
            name_bangla="অন্যান্য", alias_bangla="অন্যান্য", 
            faculty_id=no_faculty_id
        ),

        # --- Faculty of Electrical and Electronic Engineering ---
        Department(
            name_bangla="তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ", name_english="Dept of Electrical and Electronic Engineering",
            alias_bangla="ইইই", alias_english="EEE",
            faculty_id=faculty_map["তড়িৎ ও ইলেকট্রনিক কৌশল অনুষদ"]
        ),
        Department(
            name_bangla="কম্পিউটার সায়েন্স এন্ড ইঞ্জিনিয়ারিং বিভাগ", name_english="Dept of Computer Science and Engineering",
            alias_bangla="সিএসই", alias_english="CSE",
            faculty_id=faculty_map["তড়িৎ ও ইলেকট্রনিক কৌশল অনুষদ"]
        ),
        Department(
            name_bangla="বায়োমেডিক্যাল ইঞ্জিনিয়ারিং বিভাগ", name_english="Dept of Biomedical Engineering",
            alias_bangla="বিএমই", alias_english="BME",
            faculty_id=faculty_map["তড়িৎ ও ইলেকট্রনিক কৌশল অনুষদ"]
        ),

        # --- Faculty of Chemical & Materials Engineering ---
        Department(
            name_bangla="কেমিকৌশল বিভাগ", name_english="Dept of Chemical Engineering",
            alias_bangla="কেমিকৌশল", alias_english="ChE",
            faculty_id=faculty_map["কেমিক্যাল ও মেটেরিয়ালস কৌশল অনুষদ"]
        ),
        Department(
            name_bangla="বস্তু ও ধাতব কৌশল বিভাগ", name_english="Dept of Materials & Metallurgical Engineering",
            alias_bangla="এমএমই", alias_english="MME",
            faculty_id=faculty_map["কেমিক্যাল ও মেটেরিয়ালস কৌশল অনুষদ"]
        ),
        # Glass and Ceramic Engineering
        Department(
            name_bangla="গ্লাস এন্ড সিরামিক ইঞ্জিনিয়ারিং বিভাগ", name_english="Dept of Glass and Ceramic Engineering",
            alias_bangla="জিসিই", alias_english="GCE",
            faculty_id=faculty_map["কেমিক্যাল ও মেটেরিয়ালস কৌশল অনুষদ"]
        ),
        # Nanomaterials & Ceramics Engineering
        Department(
            name_bangla="ন্যানোমেটেরিয়ালস এন্ড সিরামিক ইঞ্জিনিয়ারিং বিভাগ", name_english="Dept of NCE",
            alias_bangla="এনসিই", alias_english="NCE",
            faculty_id=faculty_map["কেমিক্যাল ও মেটেরিয়ালস কৌশল অনুষদ"]
        ),

        # --- Faculty of Engineering ---
        Department(
            name_bangla="পেট্রোলিয়াম এন্ড মিনারেল রিসোর্সেস ইঞ্জিনিয়ারিং বিভাগ", name_english="Dept of PMRE",
            alias_bangla="পিএমআরই", alias_english="PMRE",
            faculty_id=faculty_map["প্রকৌশল অনুষদ"]
        ),

        # --- Faculty of Civil Engineering ---
        Department(
            name_bangla="পুরকৌশল বিভাগ", name_english="Dept of Civil Engineering",
            alias_bangla="সিই", alias_english="CE",
            faculty_id=faculty_map["পুরকৌশল অনুষদ"]
        ),
        Department(
            name_bangla="পানি সম্পদ কৌশল বিভাগ", name_english="Dept of Water Resources Engineering",
            alias_bangla="ডব্লিউআরই", alias_english="WRE",
            faculty_id=faculty_map["পুরকৌশল অনুষদ"]
        ),

        # --- Faculty of Mechanical Engineering ---
        Department(
            name_bangla="যন্ত্রকৌশল বিভাগ", name_english="Dept of Mechanical Engineering",
            alias_bangla="এমই", alias_english="ME",
            faculty_id=faculty_map["যন্ত্রকৌশল অনুষদ"]
        ),
        Department(
            name_bangla="ইন্ডাস্ট্রিয়াল এন্ড প্রোডাকশন ইঞ্জিনিয়ারিং বিভাগ", name_english="Dept of Industrial and Production Engineering",
            alias_bangla="আইপিই", alias_english="IPE",
            faculty_id=faculty_map["যন্ত্রকৌশল অনুষদ"]
        ),
        Department(
            name_bangla="নৌযান ও নৌযন্ত্র কৌশল বিভাগ", name_english="Dept of Naval Architecture and Marine Engineering",
            alias_bangla="এনএএমই", alias_english="NAME",
            faculty_id=faculty_map["যন্ত্রকৌশল অনুষদ"]
        ),

        # --- Faculty of Science ---
        Department(
            name_bangla="রসায়ন বিভাগ", name_english="Dept of Chemistry",
            alias_bangla="রসায়ন", alias_english="CHEM",
            faculty_id=faculty_map["বিজ্ঞান অনুষদ"]
        ),
        Department(
            name_bangla="গণিত বিভাগ", name_english="Dept of Mathematics",
            alias_bangla="গণিত", alias_english="MATH",
            faculty_id=faculty_map["বিজ্ঞান অনুষদ"]
        ),
        Department(
            name_bangla="পদার্থ বিজ্ঞান বিভাগ", name_english="Dept of Physics",
            alias_bangla="পদার্থ", alias_english="PHY",
            faculty_id=faculty_map["বিজ্ঞান অনুষদ"]
        ),

        # --- Faculty of Architecture and Planning ---
        Department(
            name_bangla="স্থাপত্য বিভাগ", name_english="Dept of Architecture",
            alias_bangla="স্থাপত্য", alias_english="ARCH",
            faculty_id=faculty_map["স্থাপত্য ও পরিকল্পনা অনুষদ"]
        )
    ]