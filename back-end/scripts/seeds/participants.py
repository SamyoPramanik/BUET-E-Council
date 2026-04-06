from app.models import ParticipantCard, MemberRole

def get_participant_seeds(dept_map):
    def get_id(name):
        return dept_map.get(name, dept_map["Default"])

    return [
        # ══════════════════════════════════════════════════
        # উপস্থিত সদস্যবৃন্দ — Administrative / Default
        # ══════════════════════════════════════════════════
        ParticipantCard(
            content="অধ্যাপক ডঃ সত্য প্রসাদ মজুমদার, সভাপতি, উপাচার্য, বাংলাদেশ প্রকৌশল বিশ্ববিদ্যালয়, ঢাকা।",
            role=MemberRole.REGULAR, email=None, department_id=get_id("Default")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ আব্দুল জব্বার খান, সদস্য, উপ-উপাচার্য, বাংলাদেশ প্রকৌশল বিশ্ববিদ্যালয়, ঢাকা।",
            role=MemberRole.REGULAR, email=None, department_id=get_id("Default")
        ),

        # ══════════════════════════════════════════════════
        # সকল ডীন
        # ══════════════════════════════════════════════════
        ParticipantCard(
            content="অধ্যাপক ডঃ আবু রায়হান মোহাম্মদ আলী, ডীন, যন্ত্রকৌশল অনুষদ",
            role=MemberRole.DEAN, email=None, department_id=get_id("যন্ত্রকৌশল বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ আবু সিদ্দিক, ডীন, পুরকৌশল অনুষদ",
            role=MemberRole.DEAN, email=None, department_id=get_id("পুরকৌশল বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ খন্দকার সাব্বির আহমেদ, ডীন, স্থাপত্য ও পরিকল্পনা অনুষদ",
            role=MemberRole.DEAN, email="shabbir@arch.buet.ac.bd", department_id=get_id("স্থাপত্য বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ এ্যান ফারাবি সাহা, ডীন, ডি.ই কৌশল অনুষদ",
            role=MemberRole.DEAN, email=None, department_id=get_id("Default")
        ),

        # ══════════════════════════════════════════════════
        # সকল বিভাগীয় প্রধান
        # ══════════════════════════════════════════════════
        ParticipantCard(
            content="অধ্যাপক ডঃ মাহবুর রহমান, প্রধান, কেমিকৌশল বিভাগ",
            role=MemberRole.HEAD, email=None, department_id=get_id("কেমিকৌশল বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ মাহবুব হাসান, প্রধান, বস্তু ও ধাতব কৌশল বিভাগ",
            role=MemberRole.HEAD, email="mahbubh@mme.buet.ac.bd", department_id=get_id("বস্তু ও ধাতব কৌশল বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ মো শাহাদাৎ হোসেন ফিরোজ, প্রধান, রসায়ন বিভাগ",
            role=MemberRole.HEAD, email="shfiroz@chem.buet.ac.bd", department_id=get_id("রসায়ন বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ খন্দকার ফরিদ উদ্দিন আহমেদ, প্রধান, গণিত বিভাগ",
            role=MemberRole.HEAD, email="farid@math.buet.ac.bd", department_id=get_id("গণিত বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ মো রাফি উদ্দিন, প্রধান, পদার্থ বিজ্ঞান বিভাগ",
            role=MemberRole.HEAD, email="rafiuddin@phy.buet.ac.bd", department_id=get_id("পদার্থ বিজ্ঞান বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ মো দেলোয়ার হোসেন, প্রধান, পুরকৌশল বিভাগ",
            role=MemberRole.HEAD, email=None, department_id=get_id("পুরকৌশল বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ নায়েব মো গোলাম জাকারিয়া, প্রধান, নৌযান ও নৌযন্ত্র কৌশল বিভাগ",
            role=MemberRole.HEAD, email="gzakaria@name.buet.ac.bd", department_id=get_id("নৌযান ও নৌযন্ত্র কৌশল বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ মো কামরুল হাসান, প্রধান, বি.ই কৌশল বিভাগ",
            role=MemberRole.HEAD, email="khasan@eee.buet.ac.bd", department_id=get_id("Default")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ এ.কে.এম. আনিকুর রহমান, প্রধান, সি.এস.ই বিভাগ",
            role=MemberRole.HEAD, email=None, department_id=get_id("কম্পিউটার সায়েন্স এন্ড ইঞ্জিনিয়ারিং বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ মুহ মোস্তফা উদ্দিন হাসান, প্রধান, ইউ.আর.পি বিভাগ",
            role=MemberRole.HEAD, email=None, department_id=get_id("নগর ও অঞ্চল পরিকল্পনা বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ মো ফরহাদ ইসলাম, প্রধান, গ্লাস এন্ড সিরামিক ইঞ্জিনিয়ারিং বিভাগ",
            role=MemberRole.HEAD, email=None, department_id=get_id("গ্লাস এন্ড সিরামিক ইঞ্জিনিয়ারিং বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ মো আশরাফুল হক, প্রধান, ন্যানোমেটেরিয়ালস ইঞ্জিনিয়ারিং বিভাগ",
            role=MemberRole.HEAD, email=None, department_id=get_id("ন্যানোমেটেরিয়ালস এন্ড সিরামিক ইঞ্জিনিয়ারিং বিভাগ")
        ),

        # ══════════════════════════════════════════════════
        # কেমিকৌশল বিভাগ
        # ══════════════════════════════════════════════════
        ParticipantCard(
            content="অধ্যাপক ডঃ হৈমন্তী সুলতানা রাজিয়া, সদস্য, কেমিকৌশল বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("কেমিকৌশল বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ মো আলী আহমদ শওকত চৌধুরী, সদস্য, কেমিকৌশল বিভাগ",
            role=MemberRole.REGULAR, email="shoukat@che.buet.ac.bd", department_id=get_id("কেমিকৌশল বিভাগ")
        ),
        ParticipantCard(
            content="ডঃ শেখর আহমেদ, সহযোগী অধ্যাপক, কেমিকৌশল বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("কেমিকৌশল বিভাগ")
        ),
        ParticipantCard(
            content="ডঃ কাজী ফারযীন কবীর, সহযোগী অধ্যাপক, কেমিকৌশল বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("কেমিকৌশল বিভাগ")
        ),
        ParticipantCard(
            content="ডঃ মো তানভীর সওগাত, সহযোগী অধ্যাপক, কেমিকৌশল বিভাগ",
            role=MemberRole.REGULAR, email="mstanvir@che.buet.ac.bd", department_id=get_id("কেমিকৌশল বিভাগ")
        ),
        ParticipantCard(
            content="ডঃ রাহিন সানজিদা, সহযোগী অধ্যাপক, কেমিকৌশল বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("কেমিকৌশল বিভাগ")
        ),
        ParticipantCard(
            content="ডঃ মোহাম্মদ মহিউস সামাদ খান, সহযোগী অধ্যাপক, কেমিকৌশল বিভাগ",
            role=MemberRole.REGULAR, email="mohid@che.buet.ac.bd", department_id=get_id("কেমিকৌশল বিভাগ")
        ),
        ParticipantCard(
            content="ডঃ মো ইকবাল হোসেন, সহযোগী অধ্যাপক, কেমিকৌশল বিভাগ",
            role=MemberRole.REGULAR, email="iqbalhossain@che.buet.ac.bd", department_id=get_id("কেমিকৌশল বিভাগ")
        ),
        ParticipantCard(
            content="ডঃ মো ইয়াহির আরাফাত খান, সহযোগী অধ্যাপক, কেমিকৌশল বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("কেমিকৌশল বিভাগ")
        ),

        # ══════════════════════════════════════════════════
        # বস্তু ও ধাতব কৌশল বিভাগ
        # ══════════════════════════════════════════════════
        ParticipantCard(
            content="অধ্যাপক ডঃ মো আমিনুল ইসলাম, সদস্য, বস্তু ও ধাতব কৌশল বিভাগ",
            role=MemberRole.REGULAR, email="aminulislam@mme.buet.ac.bd", department_id=get_id("বস্তু ও ধাতব কৌশল বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ ফাহমিদা গুলশান, সদস্য, বস্তু ও ধাতব কৌশল বিভাগ",
            role=MemberRole.REGULAR, email="fahmidagulshan@mme.buet.ac.bd", department_id=get_id("বস্তু ও ধাতব কৌশল বিভাগ")
        ),
        ParticipantCard(
            content="ডঃ হোসেইনি মোহাম্মদ মামুন আল রাশেদ, সহযোগী অধ্যাপক, বস্তু ও ধাতব কৌশল বিভাগ",
            role=MemberRole.REGULAR, email="hrashed@mme.buet.ac.bd", department_id=get_id("বস্তু ও ধাতব কৌশল বিভাগ")
        ),

        # ══════════════════════════════════════════════════
        # গ্লাস এন্ড সিরামিক ইঞ্জিনিয়ারিং বিভাগ
        # ══════════════════════════════════════════════════
        ParticipantCard(
            content="অধ্যাপক ডঃ মো আব্দুল মতিন, সদস্য, গ্লাস এন্ড সিরামিক ইঞ্জিনিয়ারিং বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("গ্লাস এন্ড সিরামিক ইঞ্জিনিয়ারিং বিভাগ")
        ),

        # ══════════════════════════════════════════════════
        # রসায়ন বিভাগ
        # ══════════════════════════════════════════════════
        ParticipantCard(
            content="অধ্যাপক ডঃ মো আব্দুর রশিদ, সদস্য, রসায়ন বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("রসায়ন বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ শাকিলা ব্রহ্মান, সদস্য, রসায়ন বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("রসায়ন বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ মো নজরুল ইসলাম, সদস্য, রসায়ন বিভাগ",
            role=MemberRole.REGULAR, email="islammdn@chem.buet.ac.bd", department_id=get_id("রসায়ন বিভাগ")
        ),
        ParticipantCard(
            content="মিসেস দীনা নাসরিন, সহযোগী অধ্যাপক, রসায়ন বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("রসায়ন বিভাগ")
        ),
        ParticipantCard(
            content="ডঃ আয়েশা শারমিন, সহযোগী অধ্যাপক, রসায়ন বিভাগ",
            role=MemberRole.REGULAR, email="ayeshasharmin900@chem.buet.ac.bd", department_id=get_id("রসায়ন বিভাগ")
        ),

        # ══════════════════════════════════════════════════
        # গণিত বিভাগ
        # ══════════════════════════════════════════════════
        ParticipantCard(
            content="অধ্যাপক ডঃ মো মোস্তাফিজুর রহমান, সদস্য, গণিত বিভাগ",
            role=MemberRole.REGULAR, email="mmustafizurrahman@math.buet.ac.bd", department_id=get_id("গণিত বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ মো জাফর ইকবাল খান, সদস্য, গণিত বিভাগ",
            role=MemberRole.REGULAR, email="zikhan@math.buet.ac.bd", department_id=get_id("গণিত বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ নালমা পারভীন, সদস্য, গণিত বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("গণিত বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ সালমা পারভীন, সদস্য, গণিত বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("গণিত বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ রেহেনা নাসরিন, সদস্য, গণিত বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("গণিত বিভাগ")
        ),

        # ══════════════════════════════════════════════════
        # পদার্থ বিজ্ঞান বিভাগ
        # ══════════════════════════════════════════════════
        ParticipantCard(
            content="অধ্যাপক ডঃ জীবন গোপদার, সদস্য, পদার্থ বিজ্ঞান বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("পদার্থ বিজ্ঞান বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ এ. কে.এম আতাহার হোসেন, সদস্য, পদার্থ বিজ্ঞান বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("পদার্থ বিজ্ঞান বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ মো মোশতাক হোসেন, সদস্য, পদার্থ বিজ্ঞান বিভাগ",
            role=MemberRole.REGULAR, email="mhossain@phy.buet.ac.bd", department_id=get_id("পদার্থ বিজ্ঞান বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ নাসরিন আক্তার, সদস্য, পদার্থ বিজ্ঞান বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("পদার্থ বিজ্ঞান বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ মোহাম্মদ আব্দুল বছিত, সদস্য, পদার্থ বিজ্ঞান বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("পদার্থ বিজ্ঞান বিভাগ")
        ),
        ParticipantCard(
            content="ডঃ মো আব্দুর সায়েম কাড়াল, সহযোগী অধ্যাপক, পদার্থ বিজ্ঞান বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("পদার্থ বিজ্ঞান বিভাগ")
        ),
        ParticipantCard(
            content="ডঃ মোহাম্মদ শিপ্লু রহমান, সহযোগী অধ্যাপক, পদার্থ বিজ্ঞান বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("পদার্থ বিজ্ঞান বিভাগ")
        ),
        ParticipantCard(
            content="ডঃ মোহাম্মদ সামিম উল্লাহ, সহযোগী অধ্যাপক, পদার্থ বিজ্ঞান বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("পদার্থ বিজ্ঞান বিভাগ")
        ),
        ParticipantCard(
            content="ডঃ মুহম্মদ রকিবুল ইসলাম, সহযোগী অধ্যাপক, পদার্থ বিজ্ঞান বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("পদার্থ বিজ্ঞান বিভাগ")
        ),
        ParticipantCard(
            content="ডঃ মেহনাজ শারমিন, সহযোগী অধ্যাপক, পদার্থ বিজ্ঞান বিভাগ",
            role=MemberRole.REGULAR, email="mehnaz@phy.buet.ac.bd", department_id=get_id("পদার্থ বিজ্ঞান বিভাগ")
        ),

        # ══════════════════════════════════════════════════
        # পুরকৌশল বিভাগ
        # ══════════════════════════════════════════════════
        ParticipantCard(
            content="অধ্যাপক ডঃ মো শফিউল বারী, সদস্য, পুরকৌশল বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("পুরকৌশল বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ এ.বি.এম. বদরুজ্জামান, সদস্য, পুরকৌশল বিভাগ",
            role=MemberRole.REGULAR, email="borhan@ce.buet.ac.bd", department_id=get_id("পুরকৌশল বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ ইশতিয়াক আহমেদ, সদস্য, পুরকৌশল বিভাগ",
            role=MemberRole.REGULAR, email="iahmed@ce.buet.ac.bd", department_id=get_id("পুরকৌশল বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ হাসিব মোহাম্মদ আহসান, সদস্য, পুরকৌশল বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("পুরকৌশল বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ সারওয়ার জাহান মো ইয়াহিন, সদস্য, পুরকৌশল বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("পুরকৌশল বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ বশির আহমেদ, সদস্য, পুরকৌশল বিভাগ",
            role=MemberRole.REGULAR, email="bashir@ce.buet.ac.bd", department_id=get_id("পুরকৌশল বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ খান মাহমুদ আমানত, সদস্য, পুরকৌশল বিভাগ",
            role=MemberRole.REGULAR, email="amanat@ce.buet.ac.bd", department_id=get_id("পুরকৌশল বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ মেহেদী আহমদ আনসারী, সদস্য, পুরকৌশল বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("পুরকৌশল বিভাগ")
        ),

        # ══════════════════════════════════════════════════
        # তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ (EEE)
        # ══════════════════════════════════════════════════
        ParticipantCard(
            content="অধ্যাপক ডঃ তাহমীদ মালিক আল হুসাইনী, সদস্য, তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ",
            role=MemberRole.REGULAR, email="htahmeed@yahoo.com", department_id=get_id("তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ মো মফিজুর রহমান, সদস্য, তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ",
            role=MemberRole.REGULAR, email="mafizur@gmail.com", department_id=get_id("তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ রওশন মনতাজ, সদস্য, তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ",
            role=MemberRole.REGULAR, email="mamtaz@ce.buet.ac.bd", department_id=get_id("তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ তাহসীন রেজা হোসেন, সদস্য, তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ",
            role=MemberRole.REGULAR, email="tahsin.hossain@gmail.com", department_id=get_id("তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ রাকিব আহসান, সদস্য, তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ",
            role=MemberRole.REGULAR, email="raquibahsan@ce.buet.ac.bd", department_id=get_id("তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ মো এ.ফ.এম. সাইফুল আমিন, সদস্য, তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ",
            role=MemberRole.REGULAR, email="samin@ce.buet.ac.bd", department_id=get_id("তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ মো মিজানুর রহমান, সদস্য, তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ",
            role=MemberRole.REGULAR, email="mizanurrahman@hum.buet.ac.bd", department_id=get_id("তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ মোহাম্মদ শরিফুল ইসলাম, সদস্য, তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ মাহবুবা বেগম, সদস্য, তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ",
            role=MemberRole.REGULAR, email="mahbuba@ce.buet.ac.bd", department_id=get_id("তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ মোহাম্মদ আদা আমিন সিদ্দিক, সদস্য, তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ",
            role=MemberRole.REGULAR, email="alamin@ce.buet.ac.bd", department_id=get_id("তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ")
        ),
        ParticipantCard(
            content="ডঃ শামীম আহমেদ, সহযোগী অধ্যাপক, তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ",
            role=MemberRole.REGULAR, email="shameemahmed@ce.buet.ac.bd", department_id=get_id("তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ")
        ),
        ParticipantCard(
            content="ডঃ নজরুল ইসলাম, সহযোগী অধ্যাপক, তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ",
            role=MemberRole.REGULAR, email="islammdn@chem.buet.ac.bd", department_id=get_id("তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ মো শামীম রেজা, সদস্য, তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ")
        ),
        ParticipantCard(
            content="জনাব ইয়ামিন আরাফাত, সহযোগী অধ্যাপক, তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ")
        ),
        ParticipantCard(
            content="ডঃ অদ্বিতীয় রায়, সহযোগী অধ্যাপক, তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ")
        ),
        ParticipantCard(
            content="ডঃ মাহবুব আলম, সহযোগী অধ্যাপক, তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ",
            role=MemberRole.REGULAR, email="mahbubalam@eee.buet.ac.bd", department_id=get_id("তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ")
        ),
        ParticipantCard(
            content="ডঃ নাহিন আল মাসুদ, সহযোগী অধ্যাপক, তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ")
        ),
        ParticipantCard(
            content="ডঃ মো জুনায়েদ বাতেন, সহযোগী অধ্যাপক, তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ",
            role=MemberRole.REGULAR, email="mdzunaid@eee.buet.ac.bd", department_id=get_id("তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ কাজী দীন মোহাম্মদ বশর, সদস্য, তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ মো শফিকুল ইসলাম, সদস্য, তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ",
            role=MemberRole.REGULAR, email="islams@eee.buet.ac.bd", department_id=get_id("তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ এ.বি.এম. হারুন-উর-রশিদ, সদস্য, তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ",
            role=MemberRole.REGULAR, email="abmhrashid@eee.buet.ac.bd", department_id=get_id("তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ শরীফ মোহাম্মদ মহিমুজ্জামান, সদস্য, তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ মোহাম্মদ জাহাঙ্গীর আলম, সদস্য, তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ",
            role=MemberRole.REGULAR, email="mjalam@eee.buet.ac.bd", department_id=get_id("তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ মো শাহ আলম, সদস্য, তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ",
            role=MemberRole.REGULAR, email="shalam@eee.buet.ac.bd", department_id=get_id("তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ মো জিয়াউর রহমান খান, সদস্য, তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ",
            role=MemberRole.REGULAR, email="zrkhan@eee.buet.ac.bd", department_id=get_id("তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ মোহাম্মদ ইমাহুল হাসান ভূঁঞা, সদস্য, তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ",
            role=MemberRole.REGULAR, email="imamul@eee.buet.ac.bd", department_id=get_id("তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ শেখ আশেয়ানুল ফাতাহে, সদস্য, তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ মো পেলিয়া শায়রানজ, সদস্য, তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ মোহাম্মদ আরিফুন হক, সদস্য, তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ ফাকসাসিম মাল্লান মোহাম্মদী, সদস্য, তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ সামিয়া সাবরিনা, সদস্য, তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ মো ফোরকান উদ্দিন, সদস্য, তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ",
            role=MemberRole.REGULAR, email="mforkanuddin@eee.buet.ac.bd", department_id=get_id("তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ মুক্তা আজার, সদস্য, তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ মো কাউছার আলম, সদস্য, তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ",
            role=MemberRole.REGULAR, email="kawsaralam@eee.buet.ac.bd", department_id=get_id("তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ")
        ),

        # ══════════════════════════════════════════════════
        # পানি সম্পদ কৌশল বিভাগ (WRE)
        # ══════════════════════════════════════════════════
        ParticipantCard(
            content="অধ্যাপক ডঃ মো আব্দুল মতিন, সদস্য, পানি সম্পদ কৌশল বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("পানি সম্পদ কৌশল বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ মো আতাউর রহমান, সদস্য, পানি সম্পদ কৌশল বিভাগ",
            role=MemberRole.REGULAR, email="mataur@wre.buet.ac.bd", department_id=get_id("পানি সম্পদ কৌশল বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ মোহাম্মদ মোয়াজ্জেম আলী, সদস্য, পানি সম্পদ কৌশল বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("পানি সম্পদ কৌশল বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ এ.টি.এম. হাসান জোবায়ের, সদস্য, পানি সম্পদ কৌশল বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("পানি সম্পদ কৌশল বিভাগ")
        ),

        # ══════════════════════════════════════════════════
        # যন্ত্রকৌশল বিভাগ (ME)
        # ══════════════════════════════════════════════════
        ParticipantCard(
            content="অধ্যাপক ডঃ মো মাহবুবুল আলম, সদস্য, যন্ত্রকৌশল বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("যন্ত্রকৌশল বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ মো এহসান, সদস্য, যন্ত্রকৌশল বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("যন্ত্রকৌশল বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ মোহাম্মদ আলী, সদস্য, যন্ত্রকৌশল বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("যন্ত্রকৌশল বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ মোহাম্মদ আশিকুর রহমান, সদস্য, যন্ত্রকৌশল বিভাগ",
            role=MemberRole.REGULAR, email="ashiq@me.buet.ac.bd", department_id=get_id("যন্ত্রকৌশল বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ মো আব্দুছ আলী, সদস্য, যন্ত্রকৌশল বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("যন্ত্রকৌশল বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ মুহ মাহবুব রাজ্জাক, সদস্য, যন্ত্রকৌশল বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("যন্ত্রকৌশল বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ মোহাম্মদ আরিফ হাসান মামুন, সদস্য, যন্ত্রকৌশল বিভাগ",
            role=MemberRole.REGULAR, email="arifhasan@me.buet.ac.bd", department_id=get_id("যন্ত্রকৌশল বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ মো আব্দুল সালাম আকন্দ, সদস্য, যন্ত্রকৌশল বিভাগ",
            role=MemberRole.REGULAR, email="masalamakanda@me.buet.ac.bd", department_id=get_id("যন্ত্রকৌশল বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ মোহাম্মদ মামুন, সদস্য, যন্ত্রকৌশল বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("যন্ত্রকৌশল বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ এ. বি. এম তৌফিক হাসান, সদস্য, যন্ত্রকৌশল বিভাগ",
            role=MemberRole.REGULAR, email="toufiquehasan@me.buet.ac.bd", department_id=get_id("যন্ত্রকৌশল বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ মুহাম্মদ নাসিম হায়দার, সদস্য, যন্ত্রকৌশল বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("যন্ত্রকৌশল বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ মোহাম্মদ আব্দুল মোতালেব, সদস্য, যন্ত্রকৌশল বিভাগ",
            role=MemberRole.REGULAR, email="abdulmotalab@me.buet.ac.bd", department_id=get_id("যন্ত্রকৌশল বিভাগ")
        ),
        ParticipantCard(
            content="ডঃ সুমন সাহা, সহযোগী অধ্যাপক, যন্ত্রকৌশল বিভাগ",
            role=MemberRole.REGULAR, email="sumonsaha@me.buet.ac.bd", department_id=get_id("যন্ত্রকৌশল বিভাগ")
        ),

        # ══════════════════════════════════════════════════
        # নৌযান ও নৌযন্ত্র কৌশল বিভাগ (NAME)
        # ══════════════════════════════════════════════════
        ParticipantCard(
            content="অধ্যাপক ডঃ গৌতম কুমার সাহা, সদস্য, নৌযান ও নৌযন্ত্র কৌশল বিভাগ",
            role=MemberRole.REGULAR, email="goutamkumar@name.buet.ac.bd", department_id=get_id("নৌযান ও নৌযন্ত্র কৌশল বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ মীর তারেক আলী, সদস্য, নৌযান ও নৌযন্ত্র কৌশল বিভাগ",
            role=MemberRole.REGULAR, email="mtarequeali@name.buet.ac.bd", department_id=get_id("নৌযান ও নৌযন্ত্র কৌশল বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ মো শহীদুল ইসলাম, সদস্য, নৌযান ও নৌযন্ত্র কৌশল বিভাগ",
            role=MemberRole.REGULAR, email="shahid777@name.buet.ac.bd", department_id=get_id("নৌযান ও নৌযন্ত্র কৌশল বিভাগ")
        ),
        ParticipantCard(
            content="ডঃ জোবায়ের ইবনে অওয়াল, সহযোগী অধ্যাপক, নৌযান ও নৌযন্ত্র কৌশল বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("নৌযান ও নৌযন্ত্র কৌশল বিভাগ")
        ),

        # ══════════════════════════════════════════════════
        # আই.পি.ই বিভাগ (IPE)
        # ══════════════════════════════════════════════════
        ParticipantCard(
            content="অধ্যাপক ডঃ এ কে এম মাসুদ, সদস্য, ইন্ডাস্ট্রিয়াল এন্ড প্রোডাকশন ইঞ্জিনিয়ারিং বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("ইন্ডাস্ট্রিয়াল এন্ড প্রোডাকশন ইঞ্জিনিয়ারিং বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ আব্দুল্লাহিল আজিম, সদস্য, ইন্ডাস্ট্রিয়াল এন্ড প্রোডাকশন ইঞ্জিনিয়ারিং বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("ইন্ডাস্ট্রিয়াল এন্ড প্রোডাকশন ইঞ্জিনিয়ারিং বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ সুলতানা পারভীন, সদস্য, ইন্ডাস্ট্রিয়াল এন্ড প্রোডাকশন ইঞ্জিনিয়ারিং বিভাগ",
            role=MemberRole.REGULAR, email="sparveen@ipe.buet.ac.bd", department_id=get_id("ইন্ডাস্ট্রিয়াল এন্ড প্রোডাকশন ইঞ্জিনিয়ারিং বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ এ. কে. এম. তায়েস বিন রামান, সদস্য, ইন্ডাস্ট্রিয়াল এন্ড প্রোডাকশন ইঞ্জিনিয়ারিং বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("ইন্ডাস্ট্রিয়াল এন্ড প্রোডাকশন ইঞ্জিনিয়ারিং বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ সৈয়দ মিথুন আলী, সদস্য, ইন্ডাস্ট্রিয়াল এন্ড প্রোডাকশন ইঞ্জিনিয়ারিং বিভাগ",
            role=MemberRole.REGULAR, email="mithun@ipe.buet.ac.bd", department_id=get_id("ইন্ডাস্ট্রিয়াল এন্ড প্রোডাকশন ইঞ্জিনিয়ারিং বিভাগ")
        ),
        ParticipantCard(
            content="ডঃ তত্ত্ব ঘোষ, সহযোগী অধ্যাপক, ইন্ডাস্ট্রিয়াল এন্ড প্রোডাকশন ইঞ্জিনিয়ারিং বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("ইন্ডাস্ট্রিয়াল এন্ড প্রোডাকশন ইঞ্জিনিয়ারিং বিভাগ")
        ),

        # ══════════════════════════════════════════════════
        # সি.এস.ই বিভাগ (CSE)
        # ══════════════════════════════════════════════════
        ParticipantCard(
            content="অধ্যাপক ডঃ মুহাম্মদ মাসকুর আলী, সদস্য, কম্পিউটার সায়েন্স এন্ড ইঞ্জিনিয়ারিং বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("কম্পিউটার সায়েন্স এন্ড ইঞ্জিনিয়ারিং বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ মো সাইনুর রহমান, সদস্য, কম্পিউটার সায়েন্স এন্ড ইঞ্জিনিয়ারিং বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("কম্পিউটার সায়েন্স এন্ড ইঞ্জিনিয়ারিং বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ মো মনিকল ইসলাম, সদস্য, কম্পিউটার সায়েন্স এন্ড ইঞ্জিনিয়ারিং বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("কম্পিউটার সায়েন্স এন্ড ইঞ্জিনিয়ারিং বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ মো মোস্তফা আকবর, সদস্য, কম্পিউটার সায়েন্স এন্ড ইঞ্জিনিয়ারিং বিভাগ",
            role=MemberRole.REGULAR, email="mostofa@cse.buet.ac.bd", department_id=get_id("কম্পিউটার সায়েন্স এন্ড ইঞ্জিনিয়ারিং বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক মোহাম্মদ ইউনুস আলী, সদস্য, কম্পিউটার সায়েন্স এন্ড ইঞ্জিনিয়ারিং বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("কম্পিউটার সায়েন্স এন্ড ইঞ্জিনিয়ারিং বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ মাহমুদ নাজনীন, সদস্য, কম্পিউটার সায়েন্স এন্ড ইঞ্জিনিয়ারিং বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("কম্পিউটার সায়েন্স এন্ড ইঞ্জিনিয়ারিং বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ তানজিয়া হাসেম, সদস্য, কম্পিউটার সায়েন্স এন্ড ইঞ্জিনিয়ারিং বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("কম্পিউটার সায়েন্স এন্ড ইঞ্জিনিয়ারিং বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ মোহাম্মদ শেহরাব হোসেন, সদস্য, কম্পিউটার সায়েন্স এন্ড ইঞ্জিনিয়ারিং বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("কম্পিউটার সায়েন্স এন্ড ইঞ্জিনিয়ারিং বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ এ বি এম আলিম আল ইসলাম, সদস্য, কম্পিউটার সায়েন্স এন্ড ইঞ্জিনিয়ারিং বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("কম্পিউটার সায়েন্স এন্ড ইঞ্জিনিয়ারিং বিভাগ")
        ),
        ParticipantCard(
            content="ডঃ অনিন্দ ইকবাল, সহযোগী অধ্যাপক, কম্পিউটার সায়েন্স এন্ড ইঞ্জিনিয়ারিং বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("কম্পিউটার সায়েন্স এন্ড ইঞ্জিনিয়ারিং বিভাগ")
        ),
        ParticipantCard(
            content="ডঃ রিফাত শাহরিয়ার, সহযোগী অধ্যাপক, কম্পিউটার সায়েন্স এন্ড ইঞ্জিনিয়ারিং বিভাগ",
            role=MemberRole.REGULAR, email="rifat@cse.buet.ac.bd", department_id=get_id("কম্পিউটার সায়েন্স এন্ড ইঞ্জিনিয়ারিং বিভাগ")
        ),
        ParticipantCard(
            content="ডঃ মুহাম্মদ আব্দুল্লাহ আদনান, সহযোগী অধ্যাপক, কম্পিউটার সায়েন্স এন্ড ইঞ্জিনিয়ারিং বিভাগ",
            role=MemberRole.REGULAR, email="adnan@cse.buet.ac.bd", department_id=get_id("কম্পিউটার সায়েন্স এন্ড ইঞ্জিনিয়ারিং বিভাগ")
        ),

        # ══════════════════════════════════════════════════
        # বায়োমেডিক্যাল ইঞ্জিনিয়ারিং বিভাগ (BME)
        # ══════════════════════════════════════════════════
        ParticipantCard(
            content="ডঃ মুহাম্মদ তারিক আরাফাত, সহযোগী অধ্যাপক, বায়োমেডিক্যাল ইঞ্জিনিয়ারিং বিভাগ",
            role=MemberRole.REGULAR, email="tarikarafat@bme.buet.ac.bd", department_id=get_id("বায়োমেডিক্যাল ইঞ্জিনিয়ারিং বিভাগ")
        ),

        # ══════════════════════════════════════════════════
        # স্থাপত্য বিভাগ
        # ══════════════════════════════════════════════════
        ParticipantCard(
            content="অধ্যাপক ডঃ ফরিদা নিলুফার, সদস্য, স্থাপত্য বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("স্থাপত্য বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ কাওয়ারিন চেইজী গোমেজ, সদস্য, স্থাপত্য বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("স্থাপত্য বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ মো আশিকুর রহমান জোয়ার্দার, সদস্য, স্থাপত্য বিভাগ",
            role=MemberRole.REGULAR, email="ashiq@me.buet.ac.bd", department_id=get_id("স্থাপত্য বিভাগ")
        ),
        ParticipantCard(
            content="ডঃ নাসিবা বান, সহযোগী অধ্যাপক, স্থাপত্য বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("স্থাপত্য বিভাগ")
        ),

        # ══════════════════════════════════════════════════
        # মানবিক বিভাগ
        # ══════════════════════════════════════════════════
        ParticipantCard(
            content="অধ্যাপক ডঃ আসমা বেগম, সদস্য, মানবিক বিভাগ",
            role=MemberRole.REGULAR, email="abegum@hum.buet.ac.bd", department_id=get_id("মানবিক বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ শাহনাজ পারভীন, সদস্য, মানবিক বিভাগ",
            role=MemberRole.REGULAR, email="shahnazpervin@hum.buet.ac.bd", department_id=get_id("মানবিক বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ মো মুশকিল আলম, সদস্য, মানবিক বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("মানবিক বিভাগ")
        ),

        # ══════════════════════════════════════════════════
        # নগর ও অঞ্চল পরিকল্পনা বিভাগ (URP)
        # ══════════════════════════════════════════════════
        ParticipantCard(
            content="অধ্যাপক ডঃ ইশরাত ইসলাম, সদস্য, নগর ও অঞ্চল পরিকল্পনা বিভাগ",
            role=MemberRole.REGULAR, email="ishratislam@urp.buet.ac.bd", department_id=get_id("নগর ও অঞ্চল পরিকল্পনা বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ আফসানা হক, সদস্য, নগর ও অঞ্চল পরিকল্পনা বিভাগ",
            role=MemberRole.REGULAR, email="afsanahaque@urp.buet.ac.bd", department_id=get_id("নগর ও অঞ্চল পরিকল্পনা বিভাগ")
        ),
        ParticipantCard(
            content="ডঃ আসিব-উল-জামান খান, সহযোগী অধ্যাপক, নগর ও অঞ্চল পরিকল্পনা বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("নগর ও অঞ্চল পরিকল্পনা বিভাগ")
        ),

        # ══════════════════════════════════════════════════
        # আই.ডব্লিউ.এফ.এম (IWFM)
        # ══════════════════════════════════════════════════
        ParticipantCard(
            content="অধ্যাপক ডঃ মো বেলায়ুর রহমান, সদস্য, ইনস্টিটিউট অব ওয়াটার এন্ড ফ্লাড ম্যানেজমেন্ট",
            role=MemberRole.REGULAR, email=None, department_id=get_id("ইনস্টিটিউট অব ওয়াটার এন্ড ফ্লাড ম্যানেজমেন্ট")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ মো মুনসুর রহমান, সদস্য, ইনস্টিটিউট অব ওয়াটার এন্ড ফ্লাড ম্যানেজমেন্ট",
            role=MemberRole.REGULAR, email="mmrahman@iwfm.buet.ac.bd", department_id=get_id("ইনস্টিটিউট অব ওয়াটার এন্ড ফ্লাড ম্যানেজমেন্ট")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ জি.এম. তারেকুল ইসলাম, সদস্য, ইনস্টিটিউট অব ওয়াটার এন্ড ফ্লাড ম্যানেজমেন্ট",
            role=MemberRole.REGULAR, email="tarek@iwfm.buet.ac.bd", department_id=get_id("ইনস্টিটিউট অব ওয়াটার এন্ড ফ্লাড ম্যানেজমেন্ট")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ সুরিত কুমার বালা, সদস্য, ইনস্টিটিউট অব ওয়াটার এন্ড ফ্লাড ম্যানেজমেন্ট",
            role=MemberRole.REGULAR, email=None, department_id=get_id("ইনস্টিটিউট অব ওয়াটার এন্ড ফ্লাড ম্যানেজমেন্ট")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ মুহাম্মদ শাহজাহান মন্ডল, সদস্য, ইনস্টিটিউট অব ওয়াটার এন্ড ফ্লাড ম্যানেজমেন্ট",
            role=MemberRole.REGULAR, email=None, department_id=get_id("ইনস্টিটিউট অব ওয়াটার এন্ড ফ্লাড ম্যানেজমেন্ট")
        ),

        # ══════════════════════════════════════════════════
        # আই.আই.সি.টি (IICT)
        # ══════════════════════════════════════════════════
        ParticipantCard(
            content="অধ্যাপক ডঃ মো সাইফুল ইসলাম, সদস্য, ইনস্টিটিউট অব ইনফরমেশন এন্ড কমিউনিকেশন টেকনোলজি",
            role=MemberRole.REGULAR, email="mdsaifulislam@iict.buet.ba.bd", department_id=get_id("ইনস্টিটিউট অব ইনফরমেশন এন্ড কমিউনিকেশন টেকনোলজি")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ মো লিয়াকত আলী, সদস্য, ইনস্টিটিউট অব ইনফরমেশন এন্ড কমিউনিকেশন টেকনোলজি",
            role=MemberRole.REGULAR, email="liakot@iict.buet.ac.bd", department_id=get_id("ইনস্টিটিউট অব ইনফরমেশন এন্ড কমিউনিকেশন টেকনোলজি")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ মো কবিহিয়াত হোসেন মঙ্গল, সদস্য, ইনস্টিটিউট অব ইনফরমেশন এন্ড কমিউনিকেশন টেকনোলজি",
            role=MemberRole.REGULAR, email=None, department_id=get_id("ইনস্টিটিউট অব ইনফরমেশন এন্ড কমিউনিকেশন টেকনোলজি")
        ),
        ParticipantCard(
            content="ডঃ হেসেন আসিফুল মোস্তফা, সহযোগী অধ্যাপক, ইনস্টিটিউট অব ইনফরমেশন এন্ড কমিউনিকেশন টেকনোলজি",
            role=MemberRole.REGULAR, email="hossen_mustafa@iict.buet.ac.bd", department_id=get_id("ইনস্টিটিউট অব ইনফরমেশন এন্ড কমিউনিকেশন টেকনোলজি")
        ),

        # ══════════════════════════════════════════════════
        # অন্যান্য সদস্য
        # ══════════════════════════════════════════════════
        ParticipantCard(
            content="পরিচালক, উন্নয়ন, প্রশাসন ও গবেষণা কার্যক্রম পরিষদ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("অন্যান্য")
        ),
        ParticipantCard(
            content="পরিচালক, ছাত্র কল্যাণ পরিষদ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("অন্যান্য")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ মো আবুল বাশার, প্রাক্তন মহাপরিচালক, কারিগরি শিক্ষা অধিদপ্তর, ঢাকা, ফ্ল্যাট-এ/২, হাউজ নং-৪১, রোড নং-১২৩, গুলশান-১, ঢাকা-১২১২",
            role=MemberRole.REGULAR, email=None, department_id=get_id("অন্যান্য")
        ),

        # ══════════════════════════════════════════════════
        # NEW DEANS (466 — ডীন কাজী প্রান কানাই সাহা)
        # ══════════════════════════════════════════════════
        ParticipantCard(
            content="অধ্যাপক ডঃ কাজী প্রান কানাই সাহা, ডীন, ডি.ই কৌশল অনুষদ",
            role=MemberRole.DEAN, email=None, department_id=get_id("Default")
        ),

        # ══════════════════════════════════════════════════
        # NEW HEADS (467 — পেট্রোলিয়াম এন্ড মিনারেল রিসোর্সেস)
        # ══════════════════════════════════════════════════
        ParticipantCard(
            content="অধ্যাপক ডঃ মুহ মাহবুবুর রহমান, প্রধান, পেট্রোলিয়াম এন্ড মিনারেল রিসোর্সেস ইঞ্জিনিয়ারিং বিভাগ",
            role=MemberRole.HEAD, email="mahbuburrahman@pmre.buet.ac.bd", department_id=get_id("পেট্রোলিয়াম এন্ড মিনারেল রিসোর্সেস ইঞ্জিনিয়ারিং বিভাগ")
        ),

        # ══════════════════════════════════════════════════
        # কেমিকৌশল বিভাগ — NEW (470: ডঃ কেনিশ কীর্তীয়া)
        # ══════════════════════════════════════════════════
        ParticipantCard(
            content="ডঃ কেনিশ কীর্তীয়া, সহযোগী অধ্যাপক, কেমিকৌশল বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("কেমিকৌশল বিভাগ")
        ),

        # ══════════════════════════════════════════════════
        # বস্তু ও ধাতব কৌশল বিভাগ — NEW
        # ══════════════════════════════════════════════════
        ParticipantCard(
            content="অধ্যাপক ডঃ মো মনিকুজ্জামান, সদস্য, বস্তু ও ধাতব কৌশল বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("বস্তু ও ধাতব কৌশল বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ আহমেদ শরীফ, সদস্য, বস্তু ও ধাতব কৌশল বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("বস্তু ও ধাতব কৌশল বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ কাজী মোহাম্মদ সরওয়ার্দী, সদস্য, বস্তু ও ধাতব কৌশল বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("বস্তু ও ধাতব কৌশল বিভাগ")
        ),

        # ══════════════════════════════════════════════════
        # গ্লাস এন্ড সিরামিক বিভাগ — NEW
        # ══════════════════════════════════════════════════
        ParticipantCard(
            content="ডঃ মো আবদুল্লাহ জুবায়ের, সহযোগী অধ্যাপক, গ্লাস এন্ড সিরামিক ইঞ্জিনিয়ারিং বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("গ্লাস এন্ড সিরামিক ইঞ্জিনিয়ারিং বিভাগ")
        ),

        # ══════════════════════════════════════════════════
        # রসায়ন বিভাগ — NEW
        # ══════════════════════════════════════════════════
        ParticipantCard(
            content="অধ্যাপক ডঃ আল-নকীব চৌধুরী, সদস্য, রসায়ন বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("রসায়ন বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ শাকিলা রহমান, সদস্য, রসায়ন বিভাগ",
            role=MemberRole.REGULAR, email="shaki@chem.buet.ac.bd", department_id=get_id("রসায়ন বিভাগ")
        ),

        # ══════════════════════════════════════════════════
        # গণিত বিভাগ — NEW
        # ══════════════════════════════════════════════════
        ParticipantCard(
            content="অধ্যাপক ডঃ মো মনিকুল আলম সরকার, সদস্য, গণিত বিভাগ",
            role=MemberRole.REGULAR, email="masarker@math.buet.ac.bd", department_id=get_id("গণিত বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ মো আবদুল আলীম, সদস্য, গণিত বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("গণিত বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ মো আবদুল হাকিম খান, সদস্য, গণিত বিভাগ",
            role=MemberRole.REGULAR, email="mahkhan@math.buet.ac.bd", department_id=get_id("গণিত বিভাগ")
        ),

        ParticipantCard(
            content="অধ্যাপক ডঃ নালজমা পারভীন, সদস্য, গণিত বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("গণিত বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ মোহাম্মদ ফরহাদ উদ্দিন, সদস্য, গণিত বিভাগ",
            role=MemberRole.REGULAR, email="farhad@math.buet.ac.bd", department_id=get_id("গণিত বিভাগ")
        ),

        # ══════════════════════════════════════════════════
        # পদার্থ বিজ্ঞান বিভাগ — NEW
        # ══════════════════════════════════════════════════
        ParticipantCard(
            content="অধ্যাপক ডঃ মো ফিরোজ আলম খান, সদস্য, পদার্থ বিজ্ঞান বিভাগ",
            role=MemberRole.REGULAR, email="ronin@me.buet.ac.bd", department_id=get_id("পদার্থ বিজ্ঞান বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ আফিয়া বেগম, সদস্য, পদার্থ বিজ্ঞান বিভাগ",
            role=MemberRole.REGULAR, email="apelie@phy.buet.ac.bd", department_id=get_id("পদার্থ বিজ্ঞান বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ মো আব্দুর সায়েম কাড়াল, সদস্য, পদার্থ বিজ্ঞান বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("পদার্থ বিজ্ঞান বিভাগ")
        ),

        ParticipantCard(
            content="অধ্যাপক ডঃ মো আব্দুল সায়েম ফাড়াল, সদস্য, পদার্থ বিজ্ঞান বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("পদার্থ বিজ্ঞান বিভাগ")
        ),
        ParticipantCard(
            content="ডঃ পার্জ্বলীব সুলতানা, সহযোগী অধ্যাপক, পদার্থ বিজ্ঞান বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("পদার্থ বিজ্ঞান বিভাগ")
        ),

        # ══════════════════════════════════════════════════
        # পুরকৌশল বিভাগ — NEW (467/468/469/470)
        # ══════════════════════════════════════════════════
        ParticipantCard(
            content="অধ্যাপক ডঃ মো আবদুল জলিল, সদস্য, পুরকৌশল বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("পুরকৌশল বিভাগ")
        ),

        ParticipantCard(
            content="অধ্যাপক ডঃ মো সাময্যক হক, সদস্য, পুরকৌশল বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("পুরকৌশল বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ তাহমীদ মালিক আল হুসাইনী, সদস্য, পুরকৌশল বিভাগ",
            role=MemberRole.REGULAR, email="htahmeed@yahoo.com", department_id=get_id("পুরকৌশল বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ মো মিজানুর রহমান, সদস্য, পুরকৌশল বিভাগ",
            role=MemberRole.REGULAR, email="mizanurrahman@hum.buet.ac.bd", department_id=get_id("পুরকৌশল বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ রওশন মনতাজ, সদস্য, পুরকৌশল বিভাগ",
            role=MemberRole.REGULAR, email="mamtaz@ce.buet.ac.bd", department_id=get_id("পুরকৌশল বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ তাহসীন রেজা হোসেন, সদস্য, পুরকৌশল বিভাগ",
            role=MemberRole.REGULAR, email="tahsin.hossain@gmail.com", department_id=get_id("পুরকৌশল বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ রাকিব আহসান, সদস্য, পুরকৌশল বিভাগ",
            role=MemberRole.REGULAR, email="raquibahsan@ce.buet.ac.bd", department_id=get_id("পুরকৌশল বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ মো এ.ফ.এম. সাইফুল আমিন, সদস্য, পুরকৌশল বিভাগ",
            role=MemberRole.REGULAR, email="samin@ce.buet.ac.bd", department_id=get_id("পুরকৌশল বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ মাহবুবা বেগম, সদস্য, পুরকৌশল বিভাগ",
            role=MemberRole.REGULAR, email="mahbuba@ce.buet.ac.bd", department_id=get_id("পুরকৌশল বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ মোহাম্মদ আদা আমিন সিদ্দিক, সদস্য, পুরকৌশল বিভাগ",
            role=MemberRole.REGULAR, email="alamin@ce.buet.ac.bd", department_id=get_id("পুরকৌশল বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ মোহাম্মদ শরিফুল ইসলাম, সদস্য, পুরকৌশল বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("পুরকৌশল বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ মাহবুব আলম, সদস্য, পুরকৌশল বিভাগ",
            role=MemberRole.REGULAR, email="mahbubalam@eee.buet.ac.bd", department_id=get_id("পুরকৌশল বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ মোহাম্মদ আল আমিন সিদ্দিক, সদস্য, পুরকৌশল বিভাগ",
            role=MemberRole.REGULAR, email="alamin@ce.buet.ac.bd", department_id=get_id("পুরকৌশল বিভাগ")
        ),
        ParticipantCard(
            content="ডঃ সোহেল রানা, সহযোগী অধ্যাপক, পুরকৌশল বিভাগ",
            role=MemberRole.REGULAR, email="shohel@ce.buet.ac.bd", department_id=get_id("পুরকৌশল বিভাগ")
        ),
        ParticipantCard(
            content="ডঃ শামীম আহমেদ, সহযোগী অধ্যাপক, পুরকৌশল বিভাগ",
            role=MemberRole.REGULAR, email="shameemahmed@ce.buet.ac.bd", department_id=get_id("পুরকৌশল বিভাগ")
        ),
        ParticipantCard(
            content="ডঃ নজরুল ইসলাম, সহযোগী অধ্যাপক, পুরকৌশল বিভাগ",
            role=MemberRole.REGULAR, email="islammdn@chem.buet.ac.bd", department_id=get_id("পুরকৌশল বিভাগ")
        ),

        # ══════════════════════════════════════════════════
        # যন্ত্রকৌশল বিভাগ — NEW
        # ══════════════════════════════════════════════════
        ParticipantCard(
            content="অধ্যাপক ডঃ মাগবুল আল নুর, সদস্য, যন্ত্রকৌশল বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("যন্ত্রকৌশল বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ অলোক কুমার মজুমদার, সদস্য, যন্ত্রকৌশল বিভাগ",
            role=MemberRole.REGULAR, email="aloke@me.buet.ac.bd", department_id=get_id("যন্ত্রকৌশল বিভাগ")
        ),
        ParticipantCard(
            content="ডঃ মনন মাহবুব, সহযোগী অধ্যাপক, যন্ত্রকৌশল বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("যন্ত্রকৌশল বিভাগ")
        ),

        # ══════════════════════════════════════════════════
        # নৌযান ও নৌযন্ত্র কৌশল বিভাগ — NEW
        # ══════════════════════════════════════════════════
        ParticipantCard(
            content="অধ্যাপক ডঃ মো মানসুর করিম, সদস্য, নৌযান ও নৌযন্ত্র কৌশল বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("নৌযান ও নৌযন্ত্র কৌশল বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ মো শাহজাদা তরফদার, সদস্য, নৌযান ও নৌযন্ত্র কৌশল বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("নৌযান ও নৌযন্ত্র কৌশল বিভাগ")
        ),

        # ══════════════════════════════════════════════════
        # আই.পি.ই বিভাগ — NEW
        # ══════════════════════════════════════════════════
        ParticipantCard(
            content="ডঃ মুহম্মদ আহসান আখতার হাসীন, সদস্য, ইন্ডাস্ট্রিয়াল এন্ড প্রোডাকশন ইঞ্জিনিয়ারিং বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("ইন্ডাস্ট্রিয়াল এন্ড প্রোডাকশন ইঞ্জিনিয়ারিং বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ ফেরদৌস সারোয়ার, সদস্য, ইন্ডাস্ট্রিয়াল এন্ড প্রোডাকশন ইঞ্জিনিয়ারিং বিভাগ",
            role=MemberRole.REGULAR, email="ferdoussarwar@ipe.buet.ac.bd", department_id=get_id("ইন্ডাস্ট্রিয়াল এন্ড প্রোডাকশন ইঞ্জিনিয়ারিং বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ নাহিছ আহমাদ, সদস্য, ইন্ডাস্ট্রিয়াল এন্ড প্রোডাকশন ইঞ্জিনিয়ারিং বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("ইন্ডাস্ট্রিয়াল এন্ড প্রোডাকশন ইঞ্জিনিয়ারিং বিভাগ")
        ),

        # ══════════════════════════════════════════════════
        # তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ — NEW
        # ══════════════════════════════════════════════════
        ParticipantCard(
            content="অধ্যাপক ড. প্রান কানাই সাহা, সদস্য, তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ আব্দুল হাসিব চৌধুরী, সদস্য, তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ",
            role=MemberRole.REGULAR, email="hasib@eee.buet.ac.bd", department_id=get_id("তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ")
        ),

        ParticipantCard(
            content="অধ্যাপক ডঃ মো ফরহাদ হোসেন, সদস্য, তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ লুৎফা আজার, সদস্য, তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ মো ফাউজিয়ার মোহাম্মদী, সদস্য, তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ")
        ),

        ParticipantCard(
            content="ডঃ শেখ আসিফ মাহমুদ, সহযোগী অধ্যাপক, তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ",
            role=MemberRole.REGULAR, email="asifmahmood@eee.buet.ac.bd", department_id=get_id("তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ")
        ),
        ParticipantCard(
            content="জনাব ইয়াসির আরাফাত, সহযোগী অধ্যাপক, তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ",
            role=MemberRole.REGULAR, email="arafat@eee.buet.ac.bd", department_id=get_id("তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ")
        ),
        ParticipantCard(
            content="ডঃ অপ্রিতিম রায়, সহযোগী অধ্যাপক, তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("তড়িৎ ও ইলেকট্রনিক কৌশল বিভাগ")
        ),

        # ══════════════════════════════════════════════════
        # সি.এস.ই বিভাগ — NEW
        # ══════════════════════════════════════════════════

        ParticipantCard(
            content="অধ্যাপক ডঃ আবু ছাইদ মো লতিফুল হক, সদস্য, কম্পিউটার সায়েন্স এন্ড ইঞ্জিনিয়ারিং বিভাগ",
            role=MemberRole.REGULAR, email="asmlatifulhoque@cse.buet.ac.bd", department_id=get_id("কম্পিউটার সায়েন্স এন্ড ইঞ্জিনিয়ারিং বিভাগ")
        ),

        ParticipantCard(
            content="ডঃ মো সামসুজ্জোহা রাহেজীদ, সহযোগী অধ্যাপক, কম্পিউটার সায়েন্স এন্ড ইঞ্জিনিয়ারিং বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("কম্পিউটার সায়েন্স এন্ড ইঞ্জিনিয়ারিং বিভাগ")
        ),
        ParticipantCard(
            content="ডঃ মোহাম্মদ সাইফুর রহমান, সহযোগী অধ্যাপক, কম্পিউটার সায়েন্স এন্ড ইঞ্জিনিয়ারিং বিভাগ",
            role=MemberRole.REGULAR, email="saifur@eee.buet.ac.bd", department_id=get_id("কম্পিউটার সায়েন্স এন্ড ইঞ্জিনিয়ারিং বিভাগ")
        ),

        # ══════════════════════════════════════════════════
        # স্থাপত্য বিভাগ — NEW
        # ══════════════════════════════════════════════════
        ParticipantCard(
            content="অধ্যাপক ডঃ জেবুন নাসরীন আহমদ, সদস্য, স্থাপত্য বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("স্থাপত্য বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ নাসরীন হোসেন, সদস্য, স্থাপত্য বিভাগ",
            role=MemberRole.REGULAR, email="nasreen@arch.buet.ac.bd", department_id=get_id("স্থাপত্য বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ শেখ মুহাম্মদ নাজমুল ইমাম, সদস্য, স্থাপত্য বিভাগ",
            role=MemberRole.REGULAR, email="najmul@arch.buet.ac.bd", department_id=get_id("স্থাপত্য বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ ক্যাথারিন ডেইজী গোমেজ, সদস্য, স্থাপত্য বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("স্থাপত্য বিভাগ")
        ),

        ParticipantCard(
            content="অধ্যাপক ডঃ অপূর্ব কুমার গোয়ার, সহযোগী অধ্যাপক, স্থাপত্য বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("স্থাপত্য বিভাগ")
        ),
        ParticipantCard(
            content="শেখ আহসান উল্লাহ মঙ্গলদার, সহযোগী অধ্যাপক, স্থাপত্য বিভাগ",
            role=MemberRole.REGULAR, email=None, department_id=get_id("স্থাপত্য বিভাগ")
        ),

        # ══════════════════════════════════════════════════
        # মানবিক বিভাগ — NEW
        # ══════════════════════════════════════════════════

        ParticipantCard(
            content="ডঃ মিজানুর রহমান, সহযোগী অধ্যাপক, মানবিক বিভাগ",
            role=MemberRole.REGULAR, email="mizanurrahman@hum.buet.ac.bd", department_id=get_id("মানবিক বিভাগ")
        ),

        # ══════════════════════════════════════════════════
        # নগর ও অঞ্চল পরিকল্পনা বিভাগ — NEW
        # ══════════════════════════════════════════════════
        ParticipantCard(
            content="অধ্যাপক ডঃ মোহাম্মদ শাকিল আখতার, সদস্য, নগর ও অঞ্চল পরিকল্পনা বিভাগ",
            role=MemberRole.REGULAR, email="shakil@urp.buet.ac.bd", department_id=get_id("নগর ও অঞ্চল পরিকল্পনা বিভাগ")
        ),

        # ══════════════════════════════════════════════════
        # আই.ডব্লিউ.এফ.এম (IWFM) — NEW
        # ══════════════════════════════════════════════════
        ParticipantCard(
            content="অধ্যাপক ডঃ মো রেজাউর রহমান, সদস্য, ইনস্টিটিউট অব ওয়াটার এন্ড ফ্লাড ম্যানেজমেন্ট",
            role=MemberRole.REGULAR, email=None, department_id=get_id("ইনস্টিটিউট অব ওয়াটার এন্ড ফ্লাড ম্যানেজমেন্ট")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ মো মাসিফুস সালেহীন, সদস্য, ইনস্টিটিউট অব ওয়াটার এন্ড ফ্লাড ম্যানেজমেন্ট",
            role=MemberRole.REGULAR, email=None, department_id=get_id("ইনস্টিটিউট অব ওয়াটার এন্ড ফ্লাড ম্যানেজমেন্ট")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ এ.কে.এম সাইফুল ইসলাম, সদস্য, ইনস্টিটিউট অব ওয়াটার এন্ড ফ্লাড ম্যানেজমেন্ট",
            role=MemberRole.REGULAR, email="mdsaifulislam@iict.buet.ba.bd", department_id=get_id("ইনস্টিটিউট অব ওয়াটার এন্ড ফ্লাড ম্যানেজমেন্ট")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ মোহাম্মদ আসাদ হুসাইন, সদস্য, ইনস্টিটিউট অব ওয়াটার এন্ড ফ্লাড ম্যানেজমেন্ট",
            role=MemberRole.REGULAR, email=None, department_id=get_id("ইনস্টিটিউট অব ওয়াটার এন্ড ফ্লাড ম্যানেজমেন্ট")
        ),

        # ══════════════════════════════════════════════════
        # আই.আই.সি.টি (IICT) — NEW
        # ══════════════════════════════════════════════════

        ParticipantCard(
            content="অধ্যাপক ডঃ মো কনহিয়াত হোসেন মঙ্গল, সদস্য, ইনস্টিটিউট অব ইনফরমেশন এন্ড কমিউনিকেশন টেকনোলজি",
            role=MemberRole.REGULAR, email=None, department_id=get_id("ইনস্টিটিউট অব ইনফরমেশন এন্ড কমিউনিকেশন টেকনোলজি")
        ),

        # ══════════════════════════════════════════════════
        # অন্যান্য — NEW (467: চেয়ারম্যান বিপিএসআইওআর)
        # ══════════════════════════════════════════════════
        ParticipantCard(
            content="চেয়ারম্যান, বিপিএসআইওআর, ঢাকা",
            role=MemberRole.REGULAR, email=None, department_id=get_id("অন্যান্য")
        ),
        ParticipantCard(
            content="বিভাগীয় প্রধান, পদার্থ বিজ্ঞান বিভাগ, ঢাকা বিশ্ববিদ্যালয়, ঢাকা",
            role=MemberRole.REGULAR, email=None, department_id=get_id("অন্যান্য")
        ),

        # ══════════════════════════════════════════════════
        # সিন্ডিকেট / গভর্নিং বডি — বাহ্যিক সদস্য
        # ══════════════════════════════════════════════════
        ParticipantCard(
            content="মহাপরিচালক, কারিগরি শিক্ষা অধিদপ্তর, গণপ্রজাতন্ত্রী বাংলাদেশ সরকার, এফ-৪/বি, আগারগাঁও, ঢাকা-১২০৭।",
            role=MemberRole.REGULAR, email=None, department_id=get_id("অন্যান্য")
        ),
        ParticipantCard(
            content="ডিন, ফ্যাকাল্টি অব কেমিক্যাল এন্ড ম্যাটেরিয়ালস ইঞ্জিনিয়ারিং, বাংলাদেশ প্রকৌশল বিশ্ববিদ্যালয়, ঢাকা।",
            role=MemberRole.DEAN, email=None, department_id=get_id("কেমিকৌশল বিভাগ")
        ),
        ParticipantCard(
            content="ডিন, পুরকৌশল অনুষদ, বাংলাদেশ প্রকৌশল বিশ্ববিদ্যালয়, ঢাকা।",
            role=MemberRole.DEAN, email=None, department_id=get_id("পুরকৌশল বিভাগ")
        ),
        ParticipantCard(
            content="অধ্যাপক ডঃ শাহ আব্দুল লতিফ, সাবেক সদস্য, বাংলাদেশ সরকারি কর্ম কমিশন, হাউজ-৩০, রোড-৩ (মেইন), ব্লক-ডি, সেকশন-১১, মিরপুর, ঢাকা।",
            role=MemberRole.REGULAR, email=None, department_id=get_id("অন্যান্য")
        ),
        ParticipantCard(
            content="অধ্যাপক ড. আ.আ.ম.স. আরেফিন সিদ্দিক, সাবেক উপাচার্য, ঢাকা বিশ্ববিদ্যালয়, হাউজ নং-৯৮, রোড নং-৯/এ, ধানমন্ডি আবাসিক এলাকা, ঢাকা-১২০৫।",
            role=MemberRole.REGULAR, email=None, department_id=get_id("অন্যান্য")
        ),
        ParticipantCard(
            content="জনাব মোঃ আবু ইউসুফ মিয়া, অতিরিক্ত সচিব (বিশ্ববিদ্যালয় অনুবিভাগ), মাধ্যমিক ও উচ্চ শিক্ষা বিভাগ, শিক্ষা মন্ত্রণালয়, ঢাকা।",
            role=MemberRole.REGULAR, email=None, department_id=get_id("অন্যান্য")
        ),
        ParticipantCard(
            content="জনাব অজয় দাস গুপ্ত, বীর মুক্তিযোদ্ধা ও একুশে পদক প্রাপ্ত সাংবাদিক, ফ্ল্যাট-বি৩, রোড-১, ব্লক-এ, নিকেতন হাউজিং সোসাইটি, গুলশান-১, ঢাকা-১২১২।",
            role=MemberRole.REGULAR, email=None, department_id=get_id("অন্যান্য")
        ),
        ParticipantCard(
            content="ড. জামাল উদ্দিন আহমেদ, এফসিএ, সাবেক প্রেসিডেন্ট, দি ইনস্টিটিউট অব চার্টাড একাউনটেন্ট অব বাংলাদেশ, হাউজ নং-৫১, পার্ক রোড, বারিধারা, ঢাকা।",
            role=MemberRole.REGULAR, email="farid@math.buet.ac.bd", department_id=get_id("অন্যান্য")
        ),
        ParticipantCard(
            content="অধ্যাপক ড. এস. এম. আনোয়ারা বেগম, বীর মুক্তিযোদ্ধা ও অধ্যাপক (অব:), রাষ্ট্রবিজ্ঞান বিভাগ, জগন্নাথ বিশ্ববিদ্যালয়, কৃতিকা, হাউজ#১৬৮/এ, ফ্ল্যাট#৪-সি, গ্রীন রোড, উত্তর ধানমন্ডি (কলাবাগান), ঢাকা-১২০৫।",
            role=MemberRole.REGULAR, email=None, department_id=get_id("অন্যান্য")
        ),
    ]