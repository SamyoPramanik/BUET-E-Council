import uuid
from app.models import Faculty

def get_faculty_seeds():
    return [
        # Top-level / Administrative
        Faculty(id=uuid.uuid4(), order=0, name_bangla="Default", name_english="Default"),
        
        # Academic Faculties
        Faculty(id=uuid.uuid4(), order=1, name_bangla="প্রকৌশল অনুষদ", name_english="Faculty of Engineering"),
        Faculty(id=uuid.uuid4(), order=2, name_bangla="পুরকৌশল অনুষদ", name_english="Faculty of Civil Engineering"),
        Faculty(id=uuid.uuid4(), order=3, name_bangla="তড়িৎ ও ইলেকট্রনিক কৌশল অনুষদ", name_english="Faculty of Electrical and Electronic Engineering"),
        Faculty(id=uuid.uuid4(), order=4, name_bangla="যন্ত্রকৌশল অনুষদ", name_english="Faculty of Mechanical Engineering"),
        Faculty(id=uuid.uuid4(), order=5, name_bangla="স্থাপত্য ও পরিকল্পনা অনুষদ", name_english="Faculty of Architecture and Planning"),
        Faculty(id=uuid.uuid4(), order=6, name_bangla="বিজ্ঞান অনুষদ", name_english="Faculty of Science"),
        Faculty(id=uuid.uuid4(), order=7, name_bangla="কেমিক্যাল ও মেটেরিয়ালস কৌশল অনুষদ", name_english="Faculty of Chemical & Materials Engineering"),
        
        # Catch-all
        Faculty(id=uuid.uuid4(), order=99, name_bangla="No Faculty", name_english="No Faculty")
    ]