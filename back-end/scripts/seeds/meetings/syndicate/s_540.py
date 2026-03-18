import uuid
from datetime import datetime
from app.models import Meeting

def get_seed_data():
    """Returns the data for Syndicate Meeting 540"""
    return Meeting(
        id=uuid.uuid4(),
        serial_num=540,
        is_academic=False, # Syndicate meeting
        is_finished=True,
        # Date from image: 27-12-2023, Time: 4:00 PM (16:00)
        meeting_date=datetime(2023, 12, 27, 16, 0),
        
        # Title JSON (Lexical Format)
        title={
            "root": {
                "children": [{
                    "children": [{
                        "detail": 0, "format": 1, "mode": "normal", "style": "",
                        "text": "২৭-১২-২০২৩ তারিখে অনুষ্ঠিত সিন্ডিকেটের ৫৪০তম সভা",
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
                        "text": "গত ২৭-১২-২০২৩ তারিখে সিন্ডিকেটের ৫৪০তম সভা বিকাল ৪:০০ ঘটিকায় সরাসরি ও ভার্চুয়াল (Hybrid) প্ল্যাটফর্মে মাননীয় উপাচার্য ও সিন্ডিকেটের সভাপতি অধ্যাপক ড. সত্য প্রসাদ মজুমদার-এর সভাপতিত্বে অনুষ্ঠিত হয়। সভার শুরুতে সভাপতি মহোদয় সকল সদস্যদেরকে স্বাগত জানান এবং তাঁদের সকলের সহযোগিতা কামনা করে মহান সৃষ্টিকর্তার নামে সভার কার্যক্রম শুরু করেন।",
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
                            "text": "পরিশেষে, বিভিন্ন প্রতিষ্ঠানের সাথে এই বিশ্ববিদ্যালয়ের সম্পাদিত Agreement/MoU এর বিষয়ে MoU-কমিটির সুপারিশে Agreement/MoU এর স্ট্রাকচার একই রকম থাকা বাঞ্ছনীয় বলে সভা মনে করে।",
                            "type": "text", "version": 1
                        }],
                        "direction": "ltr", "format": "justify", "indent": 0, "type": "paragraph", "version": 1
                    },
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