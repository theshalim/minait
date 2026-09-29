-- Mina IT Service — "Our Service Basket" (4 core services, English + Bangla)
-- ---------------------------------------------------------------------------
-- Written for Bangladeshi businesses: garments and factories, pharma,
-- NGOs, schools, shops and growing SMEs. Photos are free Unsplash images.
-- Edit anything later in Admin -> Services.
--
-- How to use: run db/schema.sql first, then paste this file into the
-- Supabase SQL editor and press Run. Safe to run again (existing slugs are
-- skipped). The basket is placed first on the Services page.
-- ---------------------------------------------------------------------------

-- Make room at the top: move the earlier sample services below the basket.
update services set sort_order = sort_order + 10
where slug in ('it-support-maintenance', 'office-network-setup', 'data-backup-security', 'business-email-domain')
  and sort_order < 10;

insert into services (title, title_bn, slug, category, category_bn, icon, description, description_bn, price, currency, image_url, sort_order)
select v.* from (values

  ('Custom Software Development', 'কাস্টম সফটওয়্যার ডেভেলপমেন্ট', 'custom-software-development',
   'Our Service Basket', 'আমাদের সার্ভিস বাস্কেট', 'code',
   $$Software built around the way your business already works — not the other way round. Most ready-made software is made for foreign companies; we build for how things really run here.

• Inventory, sales, accounts and HR/payroll systems for factories, pharma distributors, shops and NGOs
• Works in Bangla and English, with Bangladeshi VAT and invoice formats
• bKash, Nagad and bank payment built in, plus SMS alerts to customers and staff
• Runs on the cloud, on your own office server, or fully offline where the internet is unreliable
• You own the software and the data. We train your staff and stay on for support$$,
   $$আপনার ব্যবসা যেভাবে চলে, সেভাবেই বানানো সফটওয়্যার — উল্টোটা নয়। বেশিরভাগ রেডিমেড সফটওয়্যার বিদেশি কোম্পানির জন্য তৈরি; আমরা বানাই এখানকার বাস্তব কাজের ধারা মেনে।

• কারখানা, ফার্মা ডিস্ট্রিবিউটর, দোকান ও এনজিওর জন্য ইনভেন্টরি, সেলস, হিসাব আর এইচআর/পেরোল সিস্টেম
• বাংলা ও ইংরেজি দুই ভাষায়, বাংলাদেশের ভ্যাট ও ইনভয়েস ফরম্যাটে
• বিকাশ, নগদ ও ব্যাংক পেমেন্ট, সাথে ক্রেতা ও স্টাফদের কাছে এসএমএস অ্যালার্ট
• ক্লাউডে, আপনার অফিসের সার্ভারে, অথবা ইন্টারনেট দুর্বল হলে পুরোপুরি অফলাইনে চলে
• সফটওয়্যার আর ডেটার মালিক আপনিই। স্টাফদের ট্রেনিং দিই আর পরেও সাপোর্ট দিই$$,
   0, 'BDT', 'https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=1600&q=80&auto=format&fit=crop', 1),

  ('Web Development & Maintenance', 'ওয়েব ডেভেলপমেন্ট ও মেইনটেন্যান্স', 'web-development-maintenance',
   'Our Service Basket', 'আমাদের সার্ভিস বাস্কেট', 'globe',
   $$A fast, professional website that brings customers — and stays fast, safe and up to date after launch. Most visitors in Bangladesh come from a phone on mobile data, so we build for that first.

• Company websites, online shops, school and hospital sites, booking and portfolio sites
• Loads quickly on 4G, fully mobile-friendly, in Bangla and English
• Online orders with bKash, Nagad and card payment; Facebook Messenger and WhatsApp buttons
• Set up for Google search and Google Maps so local customers can find you
• Monthly care plan: updates, security checks, backups, small changes and uptime monitoring$$,
   $$দ্রুত, প্রফেশনাল ওয়েবসাইট যা ক্রেতা আনে — আর চালুর পরেও দ্রুত, নিরাপদ ও আপডেট থাকে। বাংলাদেশে বেশিরভাগ ভিজিটর আসেন মোবাইল ডেটায় ফোন থেকে, তাই আমরা আগে সেটার জন্যই বানাই।

• কোম্পানির ওয়েবসাইট, অনলাইন শপ, স্কুল ও হাসপাতালের সাইট, বুকিং ও পোর্টফোলিও সাইট
• ৪জি-তেও দ্রুত লোড হয়, পুরোপুরি মোবাইল-ফ্রেন্ডলি, বাংলা ও ইংরেজিতে
• বিকাশ, নগদ ও কার্ডে অনলাইন অর্ডার; ফেসবুক মেসেঞ্জার ও হোয়াটসঅ্যাপ বাটন
• গুগল সার্চ ও গুগল ম্যাপসের জন্য সেটআপ, যাতে আশপাশের ক্রেতারা খুঁজে পান
• মাসিক কেয়ার প্ল্যান: আপডেট, নিরাপত্তা চেক, ব্যাকআপ, ছোটখাটো পরিবর্তন আর সাইট চালু আছে কিনা নজরদারি$$,
   0, 'BDT', 'https://images.unsplash.com/photo-1547658719-da2b51169166?w=1600&q=80&auto=format&fit=crop', 2),

  ('Cloud Management', 'ক্লাউড ম্যানেজমেন্ট', 'cloud-management',
   'Our Service Basket', 'আমাদের সার্ভিস বাস্কেট', 'cloud',
   $$Move your files, email and business software to the cloud, so work carries on even through load-shedding, a stolen laptop or a dead office PC — and pay only for what you use.

• Google Workspace or Microsoft 365 setup: business email, shared drives and online meetings
• Servers on AWS, Google Cloud or Azure, in nearby regions like Singapore and Mumbai for speed
• Automatic daily backups, so a crashed computer never means lost work
• We watch costs every month and switch off what you don't need — no surprise dollar bills
• Staff access from home or the factory floor, with safe logins and two-step verification$$,
   $$ফাইল, ইমেইল আর ব্যবসার সফটওয়্যার ক্লাউডে নিয়ে যান, যাতে লোডশেডিং, ল্যাপটপ চুরি বা অফিসের পিসি নষ্ট হলেও কাজ থেমে না থাকে — আর খরচ করবেন শুধু যতটুকু ব্যবহার করবেন।

• গুগল ওয়ার্কস্পেস বা মাইক্রোসফট ৩৬৫ সেটআপ: বিজনেস ইমেইল, শেয়ার্ড ড্রাইভ আর অনলাইন মিটিং
• দ্রুত গতির জন্য কাছের সিঙ্গাপুর ও মুম্বাই রিজিয়নে AWS, গুগল ক্লাউড বা অ্যাজিউরে সার্ভার
• প্রতিদিন স্বয়ংক্রিয় ব্যাকআপ, তাই কম্পিউটার নষ্ট হলেও কাজ হারাবে না
• প্রতি মাসে খরচ দেখি আর অদরকারি জিনিস বন্ধ রাখি — ডলারের হঠাৎ বড় বিল নয়
• বাসা বা কারখানা থেকে স্টাফদের নিরাপদ লগইন, টু-স্টেপ ভেরিফিকেশনসহ$$,
   0, 'BDT', 'https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=1600&q=80&auto=format&fit=crop', 3),

  ('IT Infrastructure', 'আইটি ইনফ্রাস্ট্রাকচার', 'it-infrastructure',
   'Our Service Basket', 'আমাদের সার্ভিস বাস্কেট', 'chip',
   $$The solid base every office and factory needs: networks, servers, power backup and security, planned and installed properly so it just keeps working.

• Structured cabling, switches and office-wide Wi-Fi for offices, factories and multi-floor buildings
• Servers and storage, with IPS/UPS so power cuts don't take the system down
• Firewalls, CCTV, attendance and access control systems
• Multiple internet lines (ISP) with automatic switch-over when one goes down
• Clear documentation, labelled cabling and an annual maintenance contract (AMC) for peace of mind$$,
   $$প্রতিটি অফিস ও কারখানার দরকারি মজবুত ভিত্তি: নেটওয়ার্ক, সার্ভার, পাওয়ার ব্যাকআপ আর নিরাপত্তা — ঠিকমতো পরিকল্পনা করে বসানো, যাতে নিশ্চিন্তে চলতে থাকে।

• অফিস, কারখানা ও বহুতল ভবনের জন্য স্ট্রাকচার্ড ক্যাবলিং, সুইচ আর পুরো অফিসজুড়ে ওয়াই-ফাই
• সার্ভার ও স্টোরেজ, সাথে আইপিএস/ইউপিএস যাতে বিদ্যুৎ গেলেও সিস্টেম বন্ধ না হয়
• ফায়ারওয়াল, সিসিটিভি, হাজিরা ও অ্যাক্সেস কন্ট্রোল সিস্টেম
• একাধিক ইন্টারনেট লাইন (আইএসপি), একটা বন্ধ হলে নিজে থেকেই অন্যটায় চলে যায়
• পরিষ্কার ডকুমেন্টেশন, লেবেল করা ক্যাবল আর নিশ্চিন্ত থাকার জন্য বার্ষিক রক্ষণাবেক্ষণ চুক্তি (AMC)$$,
   0, 'BDT', 'https://images.unsplash.com/photo-1573164713988-8665fc963095?w=1600&q=80&auto=format&fit=crop', 4)

) as v(title, title_bn, slug, category, category_bn, icon, description, description_bn, price, currency, image_url, sort_order)
where not exists (select 1 from services s where s.slug = v.slug);
