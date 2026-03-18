import uuid
from datetime import datetime
from app.models import Meeting  # Adjust based on your actual import path

def get_seed_data():
    """Returns the data for Academic Meeting 465"""
    return Meeting(
        id=uuid.uuid4(),
        serial_num=465,
        is_academic=True,
        is_finished=True,
        meeting_date=datetime(2021, 5, 18, 11, 0),
        
        # Title JSON (Lexical Format)
        title={
            "root": {
                "children": [{
                    "children": [{
                        "detail": 0, "format": 1, "mode": "normal", "style": "",
                        "text": "১৮-০৫-২০২১ তারিখে অনুষ্ঠিত একাডেমিক কাউন্সিলের ৪৬৫তম জরুরী সভা",
                        "type": "text", "version": 1
                    }],
                    "direction": "ltr", "format": "center", "indent": 0, "type": "paragraph", "version": 1
                }],
                "direction": "ltr", "format": "", "indent": 0, "type": "root", "version": 1
            }
        },

        # Description JSON (Lexical Format)
        description={
            "root": {
                "children": [{
                    "children": [{
                        "detail": 0, "format": 0, "mode": "normal", "style": "",
                        "text": "গত ১৮-০৫-২০২১ তারিখ একাডেমিক কাউন্সিলের ৪৬৫তম জরুরী সভা সকাল ১১:০০ ঘটিকায় ভার্চুয়াল প্ল্যাটফর্মে Zoom Software এর মাধ্যমে মাননীয় উপাচার্য ও একাডেমিক কাউন্সিলের সভাপতি অধ্যাপক ডঃ সত্য প্রসাদ মজুমদার-এর সভাপতিত্বে অনুষ্ঠিত হয়। সভার শুরুতে একাডেমিক কাউন্সিলের সভাপতি সভায় উপস্থিত সকল সদস্যদেরকে স্বাগত জানান এবং তাঁদের সকলের সহযোগিতা কামনা করে মহান সৃষ্টিকর্তার নামে সভার কার্যক্রম শুরু করেন।",
                        "type": "text", "version": 1
                    }],
                    "direction": "ltr", "format": "justify", "indent": 0, "type": "paragraph", "version": 1
                }],
                "direction": "ltr", "format": "", "indent": 0, "type": "root", "version": 1
            }
        },

        # Conclusion JSON (Lexical Format)
        conclusion={
            "root": {
                "children": [{
                    "children": [{
                        "detail": 0, "format": 1, "mode": "normal", "style": "",
                        "text": "অনুমোদিত ।",
                        "type": "text", "version": 1
                    }],
                    "direction": "ltr", "format": "", "indent": 0, "type": "paragraph", "version": 1
                }],
                "direction": "ltr", "format": "", "indent": 0, "type": "root", "version": 1
            }
        }
    )