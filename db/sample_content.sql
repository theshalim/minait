-- Mina IT Service — SAMPLE content (4 services, 4 products, 4 blog posts)
-- ---------------------------------------------------------------------------
-- Demo data so the site doesn't look empty. Prices are examples. Everything
-- here can be edited or deleted in the admin panel afterwards.
--
-- How to use: run db/schema.sql first, then paste this whole file into the
-- Supabase SQL editor and press Run. Safe to run more than once: rows whose
-- slug already exists are skipped.
--
-- Images are free-to-use photos from Unsplash (unsplash.com/license).
-- ---------------------------------------------------------------------------

-- ================================ Services ================================
insert into services (title, title_bn, slug, category, description, description_bn, price, currency, image_url, sort_order)
select v.* from (values
  ('IT Support & Maintenance', 'আইটি সাপোর্ট ও মেইনটেন্যান্স', 'it-support-maintenance', 'Support',
   $$Monthly care for your office computers, printers and Wi-Fi. We fix problems remotely or on-site, keep Windows and antivirus up to date, and check everything once a month so small issues never become big ones.$$,
   $$আপনার অফিসের কম্পিউটার, প্রিন্টার ও ওয়াই-ফাইয়ের মাসিক দেখাশোনা। সমস্যা হলে রিমোট বা সরাসরি এসে সমাধান করি, উইন্ডোজ ও অ্যান্টিভাইরাস আপডেট রাখি, আর মাসে একবার সবকিছু চেক করি যাতে ছোট সমস্যা বড় না হয়।$$,
   3000, 'BDT', 'https://images.unsplash.com/photo-1486312338219-ce68d2c6f44d?w=1600&q=80&auto=format&fit=crop', 1),
  ('Office Network Setup', 'অফিস নেটওয়ার্ক সেটআপ', 'office-network-setup', 'Networking',
   $$Fast, stable internet in every corner of your office. We plan the layout, run the cables, set up routers, switches and Wi-Fi access points, and label everything so it stays easy to manage.$$,
   $$অফিসের প্রতিটি কোণে দ্রুত ও স্থির ইন্টারনেট। আমরা লেআউট প্ল্যান করি, ক্যাবল টানি, রাউটার, সুইচ ও ওয়াই-ফাই অ্যাক্সেস পয়েন্ট সেটআপ করি, আর সবকিছুতে লেবেল দিই যাতে পরে সামলানো সহজ হয়।$$,
   8000, 'BDT', 'https://images.unsplash.com/photo-1544197150-b99a580bb7a8?w=1600&q=80&auto=format&fit=crop', 2),
  ('Data Backup & Security', 'ডেটা ব্যাকআপ ও নিরাপত্তা', 'data-backup-security', 'Security',
   $$Automatic daily backups of your important files, plus firewall, antivirus and strong-password setup. If a computer dies or a virus strikes, your data is safe and we can restore it quickly.$$,
   $$জরুরি ফাইলের প্রতিদিন স্বয়ংক্রিয় ব্যাকআপ, সাথে ফায়ারওয়াল, অ্যান্টিভাইরাস ও শক্তিশালী পাসওয়ার্ড সেটআপ। কম্পিউটার নষ্ট হলে বা ভাইরাস ঢুকলেও আপনার ডেটা নিরাপদ, আর আমরা দ্রুত ফিরিয়ে আনতে পারি।$$,
   5000, 'BDT', 'https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=1600&q=80&auto=format&fit=crop', 3),
  ('Business Email & Domain', 'বিজনেস ইমেইল ও ডোমেইন', 'business-email-domain', 'Cloud',
   $$Look professional with you@yourcompany.com. We register your domain, set up business email for your team on phone and computer, and move your old emails over.$$,
   $$you@yourcompany.com দিয়ে প্রফেশনাল দেখান। আমরা ডোমেইন রেজিস্টার করি, টিমের সবার ফোন ও কম্পিউটারে বিজনেস ইমেইল সেটআপ করি, আর পুরোনো ইমেইলগুলোও নিয়ে আসি।$$,
   2500, 'BDT', 'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=1600&q=80&auto=format&fit=crop', 4)
) as v(title, title_bn, slug, category, description, description_bn, price, currency, image_url, sort_order)
where not exists (select 1 from services s where s.slug = v.slug);

-- ================================ Products ================================
insert into products (title, title_bn, slug, category, description, description_bn, price, currency, image_url, sort_order)
select v.* from (values
  ('Web Development', 'ওয়েব ডেভেলপমেন্ট', 'web-development', 'Websites',
   $$A fast, mobile-friendly website for your business — design, development, hosting setup and a simple admin panel so you can update it yourself.$$,
   $$আপনার ব্যবসার জন্য দ্রুত, মোবাইল-ফ্রেন্ডলি ওয়েবসাইট — ডিজাইন, ডেভেলপমেন্ট, হোস্টিং সেটআপ আর সহজ অ্যাডমিন প্যানেল, যাতে নিজেই আপডেট করতে পারেন।$$,
   25000, 'BDT', 'https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=1600&q=80&auto=format&fit=crop', 1),
  ('Air-Gap Software Development', 'এয়ার-গ্যাপ সফটওয়্যার ডেভেলপমেন্ট', 'air-gap-software-development', 'Software',
   $$Custom software that runs fully offline, on machines never connected to the internet — for factories, labs, banks and anywhere security matters most. Built, installed and updated by hand, with no cloud dependency.$$,
   $$সম্পূর্ণ অফলাইনে চলা কাস্টম সফটওয়্যার, এমন কম্পিউটারে যা কখনো ইন্টারনেটে যুক্ত হয় না — কারখানা, ল্যাব, ব্যাংক ও যেখানে নিরাপত্তা সবচেয়ে জরুরি। ক্লাউড ছাড়াই তৈরি, ইনস্টল ও আপডেট করা হয়।$$,
   null, 'BDT', 'https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=1600&q=80&auto=format&fit=crop', 2),
  ('Social Media Management', 'সোশ্যাল মিডিয়া ম্যানেজমেন্ট', 'social-media-management', 'Marketing',
   $$We run your Facebook and Instagram pages: 12 designed posts a month, replies to comments and messages, and a simple monthly report of what worked.$$,
   $$আপনার ফেসবুক ও ইনস্টাগ্রাম পেজ আমরা চালাই: মাসে ১২টি ডিজাইন করা পোস্ট, কমেন্ট ও মেসেজের উত্তর, আর মাস শেষে কী কাজ করল তার সহজ রিপোর্ট।$$,
   8000, 'BDT', 'https://images.unsplash.com/photo-1562577309-4932fdd64cd1?w=1600&q=80&auto=format&fit=crop', 3),
  ('Google Business Profile Setup & Management', 'গুগল বিজনেস প্রোফাইল তৈরি ও ম্যানেজমেন্ট', 'google-business-profile', 'Marketing',
   $$Get found on Google Maps and Search. We create and verify your Google Business Profile, add photos, hours and services, and keep it updated and answer reviews every month.$$,
   $$গুগল ম্যাপস ও সার্চে আপনাকে খুঁজে পাক সবাই। আমরা আপনার গুগল বিজনেস প্রোফাইল তৈরি ও ভেরিফাই করি, ছবি, সময় ও সার্ভিস যোগ করি, আর প্রতি মাসে আপডেট রাখি ও রিভিউর উত্তর দিই।$$,
   3000, 'BDT', 'https://images.unsplash.com/photo-1524661135-423995f22d0b?w=1600&q=80&auto=format&fit=crop', 4)
) as v(title, title_bn, slug, category, description, description_bn, price, currency, image_url, sort_order)
where not exists (select 1 from products p where p.slug = v.slug);

-- ================================= Blog ==================================
insert into blog_posts (title, title_bn, slug, excerpt, excerpt_bn, content_markdown, content_markdown_bn,
                        cover_image_url, is_published, is_featured, created_at)
select v.* from (values
  ('Why every local business needs a Google Business Profile',
   'কেন প্রতিটি লোকাল ব্যবসার গুগল বিজনেস প্রোফাইল দরকার',
   'why-google-business-profile',
   'When people search "near me", Google shows businesses with a profile first. Here is why it matters and how to get it right.',
   '"আমার কাছে" লিখে সার্চ করলে গুগল প্রোফাইল থাকা ব্যবসাগুলোই আগে দেখায়। কেন এটা জরুরি আর কীভাবে ঠিকমতো করবেন।',
$$Most customers now find local shops and services by searching on Google or Google Maps. If your business has no **Google Business Profile**, you simply don't show up — your competitor does.

## What a good profile gives you

- **Your place on the map**, with directions in one tap
- **Opening hours and phone number**, so people call instead of guessing
- **Photos and reviews**, which build trust before the first visit

## Three things to get right

1. **Use your real business name** — no extra keywords, or Google may suspend it.
2. **Add at least 10 good photos**: the front of your shop, inside, your team, your work.
3. **Answer every review**, good or bad, within a couple of days.

A profile takes about an hour to set up and is free. Keeping it fresh every month is what moves you up the list.$$,
$$এখন বেশিরভাগ গ্রাহক গুগল বা গুগল ম্যাপসে সার্চ করেই কাছের দোকান ও সার্ভিস খুঁজে নেন। আপনার ব্যবসার **গুগল বিজনেস প্রোফাইল** না থাকলে আপনি সার্চে আসবেন না — আসবে আপনার প্রতিযোগী।

## ভালো প্রোফাইল থেকে যা পাবেন

- **ম্যাপে আপনার জায়গা**, এক ট্যাপে রাস্তা দেখানো
- **খোলার সময় ও ফোন নম্বর**, যাতে মানুষ আন্দাজ না করে সরাসরি কল দেয়
- **ছবি ও রিভিউ**, যা প্রথমবার আসার আগেই বিশ্বাস তৈরি করে

## তিনটি জিনিস ঠিক রাখুন

1. **ব্যবসার আসল নাম দিন** — বাড়তি কিওয়ার্ড দিলে গুগল প্রোফাইল বন্ধ করে দিতে পারে।
2. **অন্তত ১০টি ভালো ছবি দিন**: দোকানের সামনে, ভেতরে, টিম, আপনার কাজ।
3. **প্রতিটি রিভিউর উত্তর দিন**, ভালো হোক বা খারাপ, দুই-এক দিনের মধ্যে।

প্রোফাইল তৈরি করতে ঘণ্টাখানেক লাগে, আর এটা ফ্রি। প্রতি মাসে আপডেট রাখলেই তালিকায় উপরে উঠবেন।$$,
   'https://images.unsplash.com/photo-1600880292203-757bb62b4baf?w=1600&q=80&auto=format&fit=crop',
   true, false, now() - interval '2 days'),

  ('5 signs your office network needs an upgrade',
   'আপনার অফিস নেটওয়ার্ক আপগ্রেড দরকার — ৫টি লক্ষণ',
   'office-network-upgrade-signs',
   'Slow video calls, dead Wi-Fi corners and a router that needs a restart every day are not normal. Here is what they tell you.',
   'ভিডিও কলে আটকে যাওয়া, অফিসের কোণে ওয়াই-ফাই না পাওয়া, প্রতিদিন রাউটার রিস্টার্ট — এগুলো স্বাভাবিক নয়। এগুলো কী বোঝায় জেনে নিন।',
$$A slow network quietly costs you hours every week. Watch for these signs:

1. **Video calls freeze** even though you pay for a fast internet package.
2. **Some rooms have no Wi-Fi**, so people crowd near the router.
3. **You restart the router every day** to make things work again.
4. **Printers and shared folders disappear** from the network at random.
5. **Nobody knows the Wi-Fi password** — or everyone, including guests, knows the same one.

## What usually fixes it

- A proper **router and switch** sized for your team
- **Access points** placed so every room gets a strong signal
- A separate **guest Wi-Fi**, so visitors never touch your office computers

Most small offices can be sorted out in a single day, with no downtime during working hours.$$,
$$ধীর নেটওয়ার্ক প্রতি সপ্তাহে চুপচাপ আপনার অনেক ঘণ্টা নষ্ট করে। এই লক্ষণগুলো খেয়াল করুন:

1. **ভিডিও কল আটকে যায়**, অথচ দ্রুত ইন্টারনেট প্যাকেজের টাকা দিচ্ছেন।
2. **কিছু রুমে ওয়াই-ফাই নেই**, তাই সবাই রাউটারের কাছে ভিড় করে।
3. **প্রতিদিন রাউটার রিস্টার্ট** করতে হয়।
4. **প্রিন্টার ও শেয়ার করা ফোল্ডার** মাঝে মাঝে নেটওয়ার্ক থেকে হারিয়ে যায়।
5. **ওয়াই-ফাই পাসওয়ার্ড কেউ জানে না** — অথবা অতিথিসহ সবাই একই পাসওয়ার্ড জানে।

## সাধারণত যা করলে ঠিক হয়

- টিমের মাপমতো ভালো **রাউটার ও সুইচ**
- এমনভাবে **অ্যাক্সেস পয়েন্ট** বসানো যাতে প্রতিটি রুমে শক্তিশালী সিগন্যাল থাকে
- আলাদা **গেস্ট ওয়াই-ফাই**, যাতে অতিথিরা অফিসের কম্পিউটারে ঢুকতে না পারে

বেশিরভাগ ছোট অফিস এক দিনেই ঠিক করা যায়, অফিস চলাকালীন কাজ না থামিয়েই।$$,
   'https://images.unsplash.com/photo-1597733336794-12d05021d510?w=1600&q=80&auto=format&fit=crop',
   true, false, now() - interval '9 days'),

  ('What is air-gapped software, and who needs it?',
   'এয়ার-গ্যাপড সফটওয়্যার কী, আর কাদের দরকার?',
   'what-is-air-gapped-software',
   'Some systems are too important to ever touch the internet. Air-gapped software is built for exactly those machines.',
   'কিছু সিস্টেম এত গুরুত্বপূর্ণ যে কখনোই ইন্টারনেটে যুক্ত করা উচিত নয়। এয়ার-গ্যাপড সফটওয়্যার ঠিক সেসব কম্পিউটারের জন্যই তৈরি।',
$$An **air-gapped** computer is one that is never connected to the internet or to any outside network. There is literally a "gap of air" between it and the rest of the world, so hackers online simply cannot reach it.

## Who uses it

- **Factories** running machines that must never stop
- **Labs and hospitals** storing sensitive records
- **Banks and offices** handling money or confidential data

## How software for it is different

- Everything it needs is **installed locally** — no cloud logins, no online licence checks.
- **Updates arrive on a checked USB drive** or disk, not over the internet.
- It keeps **its own local backups and logs**, because there is no online service to rely on.

Building for an air-gapped machine takes more planning, but in return the system is protected from almost every online attack.$$,
$$**এয়ার-গ্যাপড** কম্পিউটার হলো এমন কম্পিউটার যা কখনোই ইন্টারনেট বা বাইরের কোনো নেটওয়ার্কে যুক্ত হয় না। বাকি দুনিয়া থেকে এর মাঝে যেন "বাতাসের ফাঁক" থাকে, তাই অনলাইনের হ্যাকাররা এর নাগাল পায় না।

## কারা ব্যবহার করে

- **কারখানা**, যেখানে মেশিন কখনো থামানো যায় না
- **ল্যাব ও হাসপাতাল**, যেখানে সংবেদনশীল তথ্য থাকে
- **ব্যাংক ও অফিস**, যেখানে টাকা বা গোপন ডেটা নিয়ে কাজ হয়

## এর সফটওয়্যার কোথায় আলাদা

- দরকারি সবকিছু **কম্পিউটারেই ইনস্টল থাকে** — ক্লাউড লগইন বা অনলাইন লাইসেন্স চেক নেই।
- **আপডেট আসে যাচাই করা ইউএসবি ড্রাইভে**, ইন্টারনেটে নয়।
- **নিজস্ব ব্যাকআপ ও লগ** নিজেই রাখে, কারণ ভরসা করার মতো কোনো অনলাইন সার্ভিস নেই।

এয়ার-গ্যাপড কম্পিউটারের জন্য সফটওয়্যার বানাতে বেশি পরিকল্পনা লাগে, তবে বিনিময়ে সিস্টেমটি প্রায় সব অনলাইন আক্রমণ থেকে সুরক্ষিত থাকে।$$,
   'https://images.unsplash.com/photo-1573164713988-8665fc963095?w=1600&q=80&auto=format&fit=crop',
   true, false, now() - interval '16 days'),

  ('The 3-2-1 backup rule, explained simply',
   'সহজ ভাষায় ৩-২-১ ব্যাকআপ নিয়ম',
   'three-two-one-backup-rule',
   'Hard drives fail, laptops get stolen and viruses lock files. The 3-2-1 rule makes sure you never lose your business data.',
   'হার্ডডিস্ক নষ্ট হয়, ল্যাপটপ চুরি হয়, ভাইরাস ফাইল আটকে দেয়। ৩-২-১ নিয়ম মানলে ব্যবসার ডেটা কখনো হারাবেন না।',
$$Every business eventually loses a computer. Whether that is a small annoyance or a disaster depends on one thing: **your backups**.

## The rule

- **3 copies** of every important file (the original + 2 backups)
- on **2 different kinds of storage** (for example, the computer and an external drive)
- with **1 copy kept somewhere else** (another office, or a secure cloud)

## Easy ways to follow it

- Set backups to run **automatically every night** — manual backups get forgotten.
- **Test a restore** every few months; a backup you have never opened may not work.
- Keep the external drive **unplugged** when not in use, so a virus can't reach it too.

Setting this up usually takes an afternoon, and it can save years of work.$$,
$$প্রতিটি ব্যবসা একসময় না একসময় একটা কম্পিউটার হারায়। সেটা ছোট ঝামেলা হবে নাকি বড় বিপদ, তা নির্ভর করে একটা জিনিসের উপর: **আপনার ব্যাকআপ**।

## নিয়মটা হলো

- প্রতিটি জরুরি ফাইলের **৩টি কপি** (আসলটা + ২টি ব্যাকআপ)
- **২ ধরনের স্টোরেজে** (যেমন কম্পিউটার আর একটা এক্সটার্নাল ড্রাইভ)
- **১টি কপি অন্য জায়গায়** (আরেকটি অফিস বা নিরাপদ ক্লাউড)

## সহজে মেনে চলার উপায়

- ব্যাকআপ **প্রতি রাতে স্বয়ংক্রিয়ভাবে** চালু রাখুন — হাতে করলে ভুলে যাবেন।
- কয়েক মাস পরপর **ফাইল ফিরিয়ে এনে পরীক্ষা করুন**; কখনো না খোলা ব্যাকআপ কাজ নাও করতে পারে।
- ব্যবহার না করার সময় এক্সটার্নাল ড্রাইভ **খুলে রাখুন**, যাতে ভাইরাস সেখানেও না পৌঁছায়।

এটা সেটআপ করতে সাধারণত এক বিকেল লাগে, আর এতে বছরের পর বছরের কাজ বেঁচে যেতে পারে।$$,
   'https://images.unsplash.com/photo-1563986768609-322da13575f3?w=1600&q=80&auto=format&fit=crop',
   true, false, now() - interval '23 days')
) as v(title, title_bn, slug, excerpt, excerpt_bn, content_markdown, content_markdown_bn,
       cover_image_url, is_published, is_featured, created_at)
where not exists (select 1 from blog_posts b where b.slug = v.slug);

-- Make the Google Business Profile post the blog's big "top post", but only
-- if no top post has been picked yet.
update blog_posts set is_featured = true
where slug = 'why-google-business-profile'
  and not exists (select 1 from blog_posts where is_featured);

-- Prices are not shown on the site any more. If an earlier version of this
-- file was already run, take the price sentences out of those descriptions.
update services set description = replace(description, ' Price is per month for up to 10 computers.', ''), description_bn = replace(description_bn, ' দাম মাসিক, ১০টি কম্পিউটার পর্যন্ত।', '') where description like '%Price is per month for up to 10 computers.%' or description_bn like '%দাম মাসিক, ১০টি কম্পিউটার পর্যন্ত।%';
update services set description = replace(description, ' Starting price for a 5-page business site.', ''), description_bn = replace(description_bn, ' ৫ পেজের বিজনেস সাইটের শুরুর দাম।', '') where description like '%Starting price for a 5-page business site.%' or description_bn like '%৫ পেজের বিজনেস সাইটের শুরুর দাম।%';
update services set description = replace(description, ' Priced per project.', ''), description_bn = replace(description_bn, ' দাম প্রজেক্ট অনুযায়ী।', '') where description like '%Priced per project.%' or description_bn like '%দাম প্রজেক্ট অনুযায়ী।%';
update services set description = replace(description, ' Price is per month.', ''), description_bn = replace(description_bn, ' দাম মাসিক।', '') where description like '%Price is per month.%' or description_bn like '%দাম মাসিক।%';
update products set description = replace(description, ' Price is per month for up to 10 computers.', ''), description_bn = replace(description_bn, ' দাম মাসিক, ১০টি কম্পিউটার পর্যন্ত।', '') where description like '%Price is per month for up to 10 computers.%' or description_bn like '%দাম মাসিক, ১০টি কম্পিউটার পর্যন্ত।%';
update products set description = replace(description, ' Starting price for a 5-page business site.', ''), description_bn = replace(description_bn, ' ৫ পেজের বিজনেস সাইটের শুরুর দাম।', '') where description like '%Starting price for a 5-page business site.%' or description_bn like '%৫ পেজের বিজনেস সাইটের শুরুর দাম।%';
update products set description = replace(description, ' Priced per project.', ''), description_bn = replace(description_bn, ' দাম প্রজেক্ট অনুযায়ী।', '') where description like '%Priced per project.%' or description_bn like '%দাম প্রজেক্ট অনুযায়ী।%';
update products set description = replace(description, ' Price is per month.', ''), description_bn = replace(description_bn, ' দাম মাসিক।', '') where description like '%Price is per month.%' or description_bn like '%দাম মাসিক।%';

-- The Services page groups services by category, so give the samples two
-- shared groups (and a matching line icon each).
update services set category = 'IT Support', category_bn = 'আইটি সাপোর্ট', icon = 'support'
  where slug = 'it-support-maintenance' and (icon is null or icon = '');
update services set category = 'IT Support', category_bn = 'আইটি সাপোর্ট', icon = 'wifi'
  where slug = 'office-network-setup' and (icon is null or icon = '');
update services set category = 'Security & Cloud', category_bn = 'নিরাপত্তা ও ক্লাউড', icon = 'shield'
  where slug = 'data-backup-security' and (icon is null or icon = '');
update services set category = 'Security & Cloud', category_bn = 'নিরাপত্তা ও ক্লাউড', icon = 'email'
  where slug = 'business-email-domain' and (icon is null or icon = '');
