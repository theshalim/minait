-- Mina IT Service — FAQ for the floating "?" assistant (English + Bangla)
-- ---------------------------------------------------------------------------
-- Written for people who are NOT technical and want a website or IT help:
-- plain words, every tech term explained. Grouped by topic.
--
-- These are starting answers. Prices, timelines and payment terms here are
-- typical examples — change them in Admin -> FAQs to match how you really
-- work.
--
-- How to use: run db/schema.sql first (it adds the FAQ topic columns),
-- then paste this file into the Supabase SQL editor and press Run. Safe to
-- run again: questions that already exist are skipped.
-- ---------------------------------------------------------------------------

insert into faqs (category, category_bn, question, question_bn, answer, answer_bn, sort_order)
select v.* from (values

-- ============================= Getting started =============================
('Getting started', 'শুরু করা',
 'I know nothing about technology. Can you still help me?',
 'আমি প্রযুক্তির কিছুই বুঝি না। তবুও কি আপনারা সাহায্য করবেন?',
 $$Yes — most of our clients are not technical. You tell us about your business in plain words, we handle the technical side and explain every step simply. You never need to learn any software.$$,
 $$অবশ্যই — আমাদের বেশিরভাগ ক্লায়েন্টই টেকনিক্যাল নন। আপনি সহজ ভাষায় আপনার ব্যবসার কথা বলবেন, টেকনিক্যাল সব কাজ আমরা করব আর প্রতিটি ধাপ সহজ করে বুঝিয়ে দেব। কোনো সফটওয়্যার শেখার দরকার নেই।$$, 10),

('Getting started', 'শুরু করা',
 'How do I start?',
 'কীভাবে শুরু করব?',
 $$Tap "Get a quote" on any service or product, write a few lines about what you need, and send it. Or simply call or chat with us. We reply — usually the same day — with questions, a plan and a price.$$,
 $$যেকোনো সার্ভিস বা প্রোডাক্টে "কোটেশন নিন" চাপুন, কী দরকার দুই-এক লাইনে লিখে পাঠান। অথবা সরাসরি কল বা চ্যাট করুন। আমরা সাধারণত সেদিনই কিছু প্রশ্ন, একটা পরিকল্পনা আর দাম জানিয়ে দিই।$$, 11),

('Getting started', 'শুরু করা',
 'What should I prepare before talking to you?',
 'কথা বলার আগে আমার কী কী তৈরি রাখা উচিত?',
 $$Nothing technical. It helps if you know: what your business does, who your customers are, 2–3 websites you like, and your logo if you have one. If you don't have these, that's fine — we'll work them out together.$$,
 $$টেকনিক্যাল কিছু না। জানা থাকলে ভালো: আপনার ব্যবসা কী করে, ক্রেতা কারা, পছন্দের ২–৩টি ওয়েবসাইট, আর লোগো থাকলে সেটা। এগুলো না থাকলেও সমস্যা নেই — আমরা একসাথে ঠিক করে নেব।$$, 12),

('Getting started', 'শুরু করা',
 'Is the first consultation free?',
 'প্রথম পরামর্শ কি ফ্রি?',
 $$Yes. The first conversation and the quote are free, and you are under no obligation to go ahead.$$,
 $$হ্যাঁ। প্রথম আলাপ আর কোটেশন সম্পূর্ণ ফ্রি, আর এরপর কাজ করাতেই হবে এমন কোনো বাধ্যবাধকতা নেই।$$, 13),

-- ============================== Website basics ==============================
('Website basics', 'ওয়েবসাইট বেসিক',
 'Why does my business need a website if I already have a Facebook page?',
 'ফেসবুক পেজ তো আছে, তাহলে আলাদা ওয়েবসাইট কেন লাগবে?',
 $$A Facebook page belongs to Facebook — its rules can change and posts get buried. A website is yours: it shows up on Google, looks more trustworthy, and keeps your services, prices and contact details in one tidy place. The best setup is both, linked together.$$,
 $$ফেসবুক পেজ আসলে ফেসবুকের — নিয়ম বদলাতে পারে, পোস্ট নিচে চলে যায়। ওয়েবসাইট পুরোপুরি আপনার: গুগলে আসে, বেশি বিশ্বাসযোগ্য দেখায়, আর আপনার সার্ভিস ও যোগাযোগের তথ্য এক জায়গায় গুছিয়ে রাখে। সবচেয়ে ভালো হলো দুটোই রাখা, একটার সাথে আরেকটা যুক্ত করে।$$, 20),

('Website basics', 'ওয়েবসাইট বেসিক',
 'What kinds of websites can you build?',
 'কী ধরনের ওয়েবসাইট বানান?',
 $$Business and company websites, online shops, booking and appointment sites, school or organisation sites, blogs and custom web software. Tell us what you want people to do on the site and we'll suggest the right type.$$,
 $$ব্যবসা ও কোম্পানির ওয়েবসাইট, অনলাইন শপ, বুকিং বা অ্যাপয়েন্টমেন্টের সাইট, স্কুল বা প্রতিষ্ঠানের সাইট, ব্লগ আর কাস্টম ওয়েব সফটওয়্যার। সাইটে মানুষ কী করবে তা বলুন, আমরা সঠিক ধরনটা সাজেস্ট করব।$$, 21),

('Website basics', 'ওয়েবসাইট বেসিক',
 'Will my website work on mobile phones?',
 'আমার ওয়েবসাইট কি মোবাইলে ঠিকমতো চলবে?',
 $$Yes. Every site we build adjusts itself to phones, tablets and computers. Most of your visitors will come from a phone, so we design for phones first.$$,
 $$হ্যাঁ। আমাদের বানানো প্রতিটি সাইট ফোন, ট্যাবলেট আর কম্পিউটারে নিজে থেকেই মানিয়ে যায়। বেশিরভাগ ভিজিটর ফোন থেকেই আসবেন, তাই আমরা আগে ফোনের জন্য ডিজাইন করি।$$, 22),

('Website basics', 'ওয়েবসাইট বেসিক',
 'Can the website be in both Bangla and English?',
 'ওয়েবসাইট কি বাংলা আর ইংরেজি দুই ভাষায় হতে পারে?',
 $$Yes. Visitors can switch language with one tap, just like on this site.$$,
 $$হ্যাঁ। এই সাইটের মতোই ভিজিটর এক ট্যাপে ভাষা বদলাতে পারবেন।$$, 23),

('Website basics', 'ওয়েবসাইট বেসিক',
 'Can I change the text and pictures myself later?',
 'পরে কি আমি নিজেই লেখা আর ছবি বদলাতে পারব?',
 $$Yes. You get a simple admin panel — like filling in a form — to add products, change prices, upload photos or write posts. No coding needed, and we show you how.$$,
 $$হ্যাঁ। আপনি একটা সহজ অ্যাডমিন প্যানেল পাবেন — অনেকটা ফর্ম পূরণের মতো — যেখান থেকে প্রোডাক্ট যোগ, দাম বদল, ছবি আপলোড বা লেখা পোস্ট করতে পারবেন। কোনো কোডিং লাগবে না, আর আমরা দেখিয়ে দেব।$$, 24),

('Website basics', 'ওয়েবসাইট বেসিক',
 'Can customers order or pay online on my website?',
 'ক্রেতারা কি আমার সাইটে অনলাইনে অর্ডার বা পেমেন্ট করতে পারবেন?',
 $$Yes. We can add an order form, a shopping cart, or online payment with bKash, Nagad, cards and more through a payment gateway (a secure service that handles the money for you).$$,
 $$হ্যাঁ। অর্ডার ফর্ম, শপিং কার্ট, বা পেমেন্ট গেটওয়ের মাধ্যমে বিকাশ, নগদ, কার্ডসহ অনলাইন পেমেন্ট যোগ করা যায় (পেমেন্ট গেটওয়ে হলো একটা নিরাপদ সার্ভিস যা আপনার হয়ে টাকা লেনদেন সামলায়)।$$, 25),

-- ============================= Price & payment =============================
('Price & payment', 'দাম ও পেমেন্ট',
 'How much does a website cost?',
 'একটা ওয়েবসাইট বানাতে কত খরচ?',
 $$It depends on how many pages you need, what the site must do (for example an online shop costs more than an information site) and who writes the text and takes the photos. Send us a quick request and we'll give you a clear, fixed quote — free.$$,
 $$খরচ নির্ভর করে কত পেজ লাগবে, সাইট কী কী করবে (যেমন তথ্যের সাইটের চেয়ে অনলাইন শপে খরচ বেশি), আর লেখা-ছবি কে দেবে তার উপর। একটা ছোট রিকোয়েস্ট পাঠান, আমরা পরিষ্কার ও নির্দিষ্ট কোটেশন দেব — ফ্রি।$$, 30),

('Price & payment', 'দাম ও পেমেন্ট',
 'Are there any hidden or monthly costs?',
 'কোনো লুকানো বা মাসিক খরচ আছে কি?',
 $$No hidden costs. Every website needs a domain and hosting (explained under "Domain, hosting & email"), which are renewed once a year. We tell you these costs upfront, in the quote.$$,
 $$কোনো লুকানো খরচ নেই। প্রতিটি ওয়েবসাইটের জন্য ডোমেইন আর হোস্টিং লাগে ("ডোমেইন, হোস্টিং ও ইমেইল" অংশে বুঝিয়ে বলা আছে), যা বছরে একবার রিনিউ করতে হয়। এই খরচগুলো আমরা কোটেশনেই আগে জানিয়ে দিই।$$, 31),

('Price & payment', 'দাম ও পেমেন্ট',
 'How do I pay?',
 'পেমেন্ট কীভাবে করব?',
 $$By bKash, Nagad, bank transfer or cash. Usually part of the price is paid at the start and the rest when the work is finished and you're happy.$$,
 $$বিকাশ, নগদ, ব্যাংক ট্রান্সফার বা ক্যাশে। সাধারণত কাজ শুরুর সময় কিছু অংশ, আর কাজ শেষ হয়ে আপনি সন্তুষ্ট হলে বাকিটা দিতে হয়।$$, 32),

('Price & payment', 'দাম ও পেমেন্ট',
 'Will I get a written quote and a receipt?',
 'লিখিত কোটেশন আর রসিদ পাব কি?',
 $$Yes. You get a written quote that lists exactly what's included, and a receipt for every payment. You also get a tracking link to check the status of your request any time.$$,
 $$হ্যাঁ। কী কী থাকবে তা পরিষ্কার লেখা একটা লিখিত কোটেশন পাবেন, আর প্রতিটি পেমেন্টের রসিদ। যেকোনো সময় অবস্থা দেখার জন্য একটা ট্র্যাকিং লিংকও পাবেন।$$, 33),

-- ============================== Time & process ==============================
('Time & process', 'সময় ও কাজের ধাপ',
 'How long does it take to make a website?',
 'ওয়েবসাইট বানাতে কত দিন লাগে?',
 $$A simple business website usually takes 1–2 weeks. An online shop or custom software takes longer — often 3–8 weeks. The biggest factor is how quickly we get your text and photos.$$,
 $$একটা সাধারণ বিজনেস ওয়েবসাইটে সাধারণত ১–২ সপ্তাহ লাগে। অনলাইন শপ বা কাস্টম সফটওয়্যারে বেশি সময় লাগে — প্রায়ই ৩–৮ সপ্তাহ। সবচেয়ে বড় বিষয় হলো আপনার লেখা আর ছবি আমরা কত দ্রুত পাই।$$, 40),

('Time & process', 'সময় ও কাজের ধাপ',
 'What are the steps, from idea to a live website?',
 'আইডিয়া থেকে চালু ওয়েবসাইট পর্যন্ত ধাপগুলো কী?',
 $$1) We talk and understand your needs. 2) You get a quote and plan. 3) We show you a design to approve. 4) We build the site and you review it. 5) We make your changes. 6) The site goes live and we show you how to use it.$$,
 $$১) আলাপ করে আপনার প্রয়োজন বুঝি। ২) কোটেশন আর পরিকল্পনা পাঠাই। ৩) অনুমোদনের জন্য ডিজাইন দেখাই। ৪) সাইট বানাই, আপনি দেখে নেন। ৫) আপনার বলা পরিবর্তনগুলো করি। ৬) সাইট চালু করি আর কীভাবে ব্যবহার করবেন দেখিয়ে দিই।$$, 41),

('Time & process', 'সময় ও কাজের ধাপ',
 'Can I see the design before you build it?',
 'বানানোর আগে কি ডিজাইন দেখতে পারব?',
 $$Yes. We show you the design first and only start building after you approve it. Your changes are included.$$,
 $$হ্যাঁ। আগে ডিজাইন দেখাই, আপনি অনুমোদন দিলেই বানানো শুরু করি। আপনার পরিবর্তনগুলো এর মধ্যেই ধরা থাকে।$$, 42),

('Time & process', 'সময় ও কাজের ধাপ',
 'What if I don''t like something?',
 'কিছু পছন্দ না হলে কী হবে?',
 $$Tell us — we change it. Rounds of changes are included in every project, and we keep adjusting until the site feels right to you.$$,
 $$জানান — আমরা বদলে দেব। প্রতিটি প্রজেক্টে কয়েক দফা পরিবর্তন ধরা থাকে, আর আপনার মনমতো না হওয়া পর্যন্ত আমরা ঠিক করতে থাকি।$$, 43),

-- ========================= Domain, hosting & email =========================
('Domain, hosting & email', 'ডোমেইন, হোস্টিং ও ইমেইল',
 'What is a domain?',
 'ডোমেইন কী?',
 $$A domain is your website's address, like yourshop.com — what people type to find you. You pay for it once a year to keep it. We help you choose and register one in your name.$$,
 $$ডোমেইন হলো আপনার ওয়েবসাইটের ঠিকানা, যেমন yourshop.com — যা লিখে মানুষ আপনাকে খুঁজে পায়। এটা রাখতে বছরে একবার টাকা দিতে হয়। আমরা আপনার নামে পছন্দ করে রেজিস্টার করতে সাহায্য করি।$$, 50),

('Domain, hosting & email', 'ডোমেইন, হোস্টিং ও ইমেইল',
 'What is hosting?',
 'হোস্টিং কী?',
 $$Hosting is the computer (server) on the internet where your website lives, so it is open 24/7. Think of the domain as your address and hosting as the shop building. We set it up and look after it for you.$$,
 $$হোস্টিং হলো ইন্টারনেটের সেই কম্পিউটার (সার্ভার) যেখানে আপনার ওয়েবসাইট রাখা থাকে, যাতে সেটা ২৪ ঘণ্টা খোলা থাকে। ডোমেইন যদি ঠিকানা হয়, হোস্টিং হলো দোকানের ঘর। আমরা এটা সেটআপ করি আর দেখাশোনা করি।$$, 51),

('Domain, hosting & email', 'ডোমেইন, হোস্টিং ও ইমেইল',
 'Will the website and domain be in my name?',
 'ওয়েবসাইট আর ডোমেইন কি আমার নামে থাকবে?',
 $$Yes. The domain is registered in your name and the website belongs to you. We hand over all logins and passwords at the end.$$,
 $$হ্যাঁ। ডোমেইন আপনার নামে রেজিস্টার হয় আর ওয়েবসাইটের মালিক আপনিই। কাজ শেষে সব লগইন আর পাসওয়ার্ড আপনাকে বুঝিয়ে দিই।$$, 52),

('Domain, hosting & email', 'ডোমেইন, হোস্টিং ও ইমেইল',
 'Can I get an email like info@mycompany.com?',
 'info@mycompany.com এর মতো ইমেইল কি পাব?',
 $$Yes. We set up business email with your own domain, on your phone and computer. It looks far more professional than a free Gmail address.$$,
 $$হ্যাঁ। আপনার নিজের ডোমেইন দিয়ে বিজনেস ইমেইল সেটআপ করে দিই, ফোন আর কম্পিউটার দুটোতেই। ফ্রি জিমেইলের চেয়ে এটা অনেক বেশি প্রফেশনাল দেখায়।$$, 53),

('Domain, hosting & email', 'ডোমেইন, হোস্টিং ও ইমেইল',
 'I already have a website. Can you fix or redesign it?',
 'আমার আগে থেকেই একটা ওয়েবসাইট আছে। ঠিক বা নতুন করে ডিজাইন করে দেবেন?',
 $$Yes. We can fix problems, speed it up, move it to better hosting, or give it a fresh modern design while keeping your address and content.$$,
 $$হ্যাঁ। সমস্যা ঠিক করা, সাইট দ্রুত করা, ভালো হোস্টিংয়ে সরানো, অথবা ঠিকানা আর লেখা ঠিক রেখে আধুনিক নতুন ডিজাইন — সবই করি।$$, 54),

-- ========================== After launch & support ==========================
('After launch & support', 'লঞ্চের পর সাপোর্ট',
 'What happens after my website goes live?',
 'ওয়েবসাইট চালু হওয়ার পর কী হয়?',
 $$We show you how to update it, and we stay available. Every project includes free support for a period after launch to fix any problems. After that you can choose a small monthly care plan, or just call us when you need something.$$,
 $$কীভাবে আপডেট করবেন দেখিয়ে দিই, আর আমরা পাশে থাকি। প্রতিটি প্রজেক্টে চালুর পর একটা সময় পর্যন্ত ফ্রি সাপোর্ট থাকে, কোনো সমস্যা হলে ঠিক করে দিই। এরপর চাইলে ছোট একটা মাসিক কেয়ার প্ল্যান নিতে পারেন, অথবা দরকার হলে শুধু ফোন করবেন।$$, 60),

('After launch & support', 'লঞ্চের পর সাপোর্ট',
 'What if the website stops working?',
 'ওয়েবসাইট হঠাৎ কাজ না করলে কী করব?',
 $$Call or message us. We check it quickly and fix it. Because we keep backups of your site, it can always be restored.$$,
 $$আমাদের কল বা মেসেজ দিন। আমরা দ্রুত দেখে ঠিক করে দেব। আপনার সাইটের ব্যাকআপ রাখা থাকে, তাই সবসময় ফিরিয়ে আনা যায়।$$, 61),

('After launch & support', 'লঞ্চের পর সাপোর্ট',
 'Do you train me or my staff?',
 'আমাকে বা আমার স্টাফদের কি শিখিয়ে দেবেন?',
 $$Yes. We give a short, friendly training session and a simple guide, and you can ask us questions any time.$$,
 $$হ্যাঁ। ছোট একটা সহজ ট্রেনিং সেশন আর একটা সহজ গাইড দিই, আর যেকোনো সময় প্রশ্ন করতে পারবেন।$$, 62),

-- ============================= Security & safety =============================
('Security & safety', 'নিরাপত্তা',
 'Is my website safe from hackers?',
 'আমার ওয়েবসাইট কি হ্যাকারদের থেকে নিরাপদ?',
 $$We protect every site with SSL (the padlock in the browser that keeps data private), strong passwords, regular updates and backups. No website can be 100% hack-proof, but these steps block almost all common attacks.$$,
 $$প্রতিটি সাইট আমরা SSL (ব্রাউজারের তালা চিহ্ন, যা তথ্য গোপন রাখে), শক্তিশালী পাসওয়ার্ড, নিয়মিত আপডেট আর ব্যাকআপ দিয়ে সুরক্ষিত রাখি। কোনো সাইটই ১০০% হ্যাক-প্রুফ নয়, তবে এই ব্যবস্থাগুলো প্রায় সব সাধারণ আক্রমণ ঠেকায়।$$, 70),

('Security & safety', 'নিরাপত্তা',
 'Is my customers'' information kept private?',
 'আমার ক্রেতাদের তথ্য কি গোপন থাকবে?',
 $$Yes. Customer details are stored securely, only you and your team can see them, and we never share them with anyone.$$,
 $$হ্যাঁ। ক্রেতাদের তথ্য নিরাপদে রাখা হয়, শুধু আপনি আর আপনার টিম দেখতে পারবেন, আর আমরা কারো সাথে শেয়ার করি না।$$, 71),

-- ============================ Marketing & Google ============================
('Marketing & Google', 'মার্কেটিং ও গুগল',
 'Will my website show up on Google?',
 'আমার ওয়েবসাইট কি গুগলে আসবে?',
 $$Yes. We build every site so Google can read it easily (this is called SEO) and submit it to Google. Reaching the very top for busy search words takes time and regular content, and we can help with that too.$$,
 $$হ্যাঁ। প্রতিটি সাইট এমনভাবে বানাই যাতে গুগল সহজে পড়তে পারে (একে SEO বলে), আর গুগলে জমা দিই। জনপ্রিয় সার্চ শব্দে একেবারে উপরে আসতে সময় আর নিয়মিত লেখা লাগে — সেটাতেও আমরা সাহায্য করতে পারি।$$, 80),

('Marketing & Google', 'মার্কেটিং ও গুগল',
 'What is a Google Business Profile, and do I need one?',
 'গুগল বিজনেস প্রোফাইল কী, এটা কি আমার দরকার?',
 $$It's the box that shows your business on Google Maps and Search — with your address, phone, opening hours, photos and reviews. If customers visit or call you, it is one of the most useful free things you can have. We create and manage it for you.$$,
 $$এটা হলো গুগল ম্যাপস আর সার্চে আপনার ব্যবসার বক্স — ঠিকানা, ফোন, খোলার সময়, ছবি আর রিভিউসহ। ক্রেতারা যদি আপনার কাছে আসেন বা ফোন করেন, তাহলে এটা সবচেয়ে কাজের ফ্রি জিনিসগুলোর একটি। আমরা এটা তৈরি করে দেখাশোনা করি।$$, 81),

('Marketing & Google', 'মার্কেটিং ও গুগল',
 'Can you run my Facebook and Instagram pages?',
 'আমার ফেসবুক আর ইনস্টাগ্রাম পেজ কি আপনারা চালাবেন?',
 $$Yes. We plan and design posts, reply to comments and messages, and send you a simple monthly report of what worked.$$,
 $$হ্যাঁ। পোস্ট পরিকল্পনা ও ডিজাইন করি, কমেন্ট আর মেসেজের উত্তর দিই, আর মাস শেষে কী কাজ করল তার সহজ রিপোর্ট পাঠাই।$$, 82),

-- ============================== Other services ==============================
('Other services', 'অন্যান্য সার্ভিস',
 'Do you also fix computers, Wi-Fi and office networks?',
 'কম্পিউটার, ওয়াই-ফাই আর অফিস নেটওয়ার্কও কি ঠিক করেন?',
 $$Yes. We set up and repair office computers, printers, Wi-Fi and networks, and offer monthly IT support so you have someone to call whenever something goes wrong.$$,
 $$হ্যাঁ। অফিসের কম্পিউটার, প্রিন্টার, ওয়াই-ফাই আর নেটওয়ার্ক সেটআপ ও মেরামত করি, আর মাসিক আইটি সাপোর্ট দিই যাতে সমস্যা হলেই ফোন করার মতো কেউ থাকে।$$, 90),

('Other services', 'অন্যান্য সার্ভিস',
 'What is "air-gap software", in simple words?',
 'সহজ ভাষায় "এয়ার-গ্যাপ সফটওয়্যার" কী?',
 $$Software that runs on computers that are never connected to the internet, so hackers online can't reach them. Factories, labs and banks use it for their most important systems. We build and install it for them.$$,
 $$এমন সফটওয়্যার যা কখনো ইন্টারনেটে যুক্ত না থাকা কম্পিউটারে চলে, তাই অনলাইনের হ্যাকাররা নাগাল পায় না। কারখানা, ল্যাব আর ব্যাংক তাদের সবচেয়ে গুরুত্বপূর্ণ সিস্টেমে এটা ব্যবহার করে। আমরা এটা বানিয়ে ইনস্টল করে দিই।$$, 91),

('Other services', 'অন্যান্য সার্ভিস',
 'Can I see a demo before I decide?',
 'সিদ্ধান্ত নেওয়ার আগে কি ডেমো দেখতে পারব?',
 $$Yes. On any product, tap "Book a demo", pick a time that suits you, and we'll show you how it works — online or in person.$$,
 $$হ্যাঁ। যেকোনো প্রোডাক্টে "ডেমো বুক করুন" চাপুন, সুবিধামতো সময় বেছে নিন, আমরা অনলাইনে বা সরাসরি দেখিয়ে দেব কীভাবে কাজ করে।$$, 92),

('Other services', 'অন্যান্য সার্ভিস',
 'Do you work only in Bangladesh?',
 'আপনারা কি শুধু বাংলাদেশে কাজ করেন?',
 $$Most of our clients are in Bangladesh, but websites, software and online services can be done for clients anywhere. On-site work like networks and CCTV is done locally.$$,
 $$আমাদের বেশিরভাগ ক্লায়েন্ট বাংলাদেশে, তবে ওয়েবসাইট, সফটওয়্যার আর অনলাইন সার্ভিস যেকোনো দেশের ক্লায়েন্টের জন্য করা যায়। নেটওয়ার্ক বা সিসিটিভির মতো সরাসরি কাজ স্থানীয়ভাবে করা হয়।$$, 93)

) as v(category, category_bn, question, question_bn, answer, answer_bn, sort_order)
where not exists (select 1 from faqs f where f.question = v.question);
