import uuid
from datetime import datetime
from app.models import Meeting

def get_seed_data():
    """Returns the data for Academic Meeting 468"""
    return Meeting(
        id=uuid.uuid4(),
        serial_num=468,
        is_academic=True,
        is_finished=True,
        # Date from image: 28-07-2021, Time: 4:00 PM (16:00)
        meeting_date=datetime(2021, 7, 28, 16, 0),
        
        # Title JSON (Lexical Format)
        title={
            "root": {
                "children": [{
                    "children": [{
                        "detail": 0, "format": 1, "mode": "normal", "style": "",
                        "text": "২৮-০৭-২০২১ তারিখে অনুষ্ঠিত একাডেমিক কাউন্সিলের ৪৬৮তম সভা",
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
                        "text": "গত ২৮-০৭-২০২১ তারিখ একাডেমিক কাউন্সিলের ৪৬৮-তম সভা বিকাল ৪:০০ ঘটিকায় ভার্চুয়াল প্ল্যাটফর্মে Zoom Software এর মাধ্যমে মাননীয় উপাচার্য ও একাডেমিক কাউন্সিলের সভাপতি অধ্যাপক ডঃ সত্য প্রসাদ মজুমদার-এর সভাপতিত্বে অনুষ্ঠিত হয়। সভার শুরুতে সভাপতি মহোদয় সকল সদস্যদেরকে স্বাগত জানান এবং সকলের সহযোগিতা কামনা করে মহান সৃষ্টিকর্তার নামে সভার কার্যক্রম শুরু করেন।",
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
                "children": [
                    {
                        "children": [{
                            "detail": 0, "format": 0, "mode": "normal", "style": "",
                            "text": "পরিশেষে, সভাপতি মহোদয় সভায় উপস্থিত সকলকে ধন্যবাদ জানিয়ে সভার কার্য সমাপ্তি ঘোষণা করেন।",
                            "type": "text", "version": 1
                        }],
                        "direction": "ltr", "format": "justify", "indent": 0, "type": "paragraph", "version": 1
                    },
                    {
                        "children": [{
                            "detail": 0, "format": 1, "mode": "normal", "style": "",
                            "text": "অনুমোদিত ।",
                            "type": "text", "version": 1
                        }],
                        "direction": "ltr", "format": "", "indent": 0, "type": "paragraph", "version": 1
                    }
                ],
                "direction": "ltr", "format": "", "indent": 0, "type": "root", "version": 1
            }
        }
    )