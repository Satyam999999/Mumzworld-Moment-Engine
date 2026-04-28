import json, os

MILESTONES = [
    ("MS-001","Starting Solids","بداية الأكل الصلب",180,30,"Baby ready for pureed/soft foods","baby first foods weaning starter kit solid feeding","BPA-free products only. No honey before 12 months."),
    ("MS-002","Tummy Time / Rolling Over","الوقت على البطن والتقلب",90,20,"Baby developing neck/core strength","tummy time mat play gym activity baby","Ensure flat safe surface."),
    ("MS-003","Sitting Unsupported","الجلوس بدون دعم",180,20,"Baby learning to sit independently","baby seat support pillow activity chair","Never leave unsupported on elevated surfaces."),
    ("MS-004","First Steps / Walking","الخطوات الأولى",365,30,"Baby beginning to walk","baby first walker push toy walking shoes","Soft-soled shoes recommended."),
    ("MS-005","Transition from Bassinet to Crib","الانتقال من المهد إلى السرير",90,20,"Baby outgrowing bassinet","baby crib toddler bed mattress sleep safe","Firm mattress, no loose bedding."),
    ("MS-006","Dropping Night Feeds","التوقف عن الرضاعة الليلية",120,20,"Baby sleeping longer stretches","baby sleep aid white noise soother","Consult pediatrician before stopping feeds."),
    ("MS-007","Starting Day Care / Nursery","بداية الحضانة",270,30,"Baby starting nursery or day care","nursery bag diaper bag baby essentials daycare","Label all items."),
    ("MS-008","Moving to Forward-Facing Car Seat","الانتقال لمقعد السيارة الأمامي",365,30,"Child ready for forward-facing seat","forward facing car seat toddler safety","Must meet weight/height minimums."),
    ("MS-009","Transition to Sippy Cup","الانتقال لكوب الشفاطة",180,30,"Baby learning to drink from cup","sippy cup trainer cup baby drinking weaning","BPA-free only."),
    ("MS-010","First Teeth / Teething Peak","ذروة التسنين",150,20,"Baby teething begins","teething ring gel soother chew toy baby","No aspirin. Use teething-safe products."),
    ("MS-011","Bath Seat Transition","الانتقال لكرسي الاستحمام",150,20,"Baby ready for bath seat","baby bath seat ring support tub","Never leave unattended in water."),
    ("MS-012","Potty Training Readiness","الاستعداد لتدريب الحمام",540,30,"Toddler showing potty readiness signs","potty training seat toilet toddler step stool","Child-led approach recommended."),
    ("MS-013","Toddler Bed Transition","الانتقال لسرير الأطفال الصغار",540,30,"Child moving from crib to toddler bed","toddler bed rail guard mattress sleep","Use bed rail for safety."),
    ("MS-014","First Backpack / Nursery Bag","أول حقيبة ظهر",900,30,"Child starting to carry own bag","toddler backpack nursery bag kids school","Lightweight, ergonomic."),
    ("MS-015","Outdoor / Tricycle Stage","مرحلة الدراجة ثلاثية العجلات",730,30,"Child ready for outdoor riding toys","tricycle balance bike outdoor toddler ride","Helmet required."),
    ("MS-016","Arts and Crafts Stage","مرحلة الفنون والحرف",1095,30,"Child ready for creative play","art craft kit toddler paint clay non-toxic","Non-toxic materials only."),
    ("MS-017","Transition from Stroller to Walking","التحول من العربة للمشي",548,30,"Toddler preferring to walk","lightweight stroller travel toddler buggy","Keep stroller for long trips."),
    ("MS-018","Toothbrushing Introduction","بداية تنظيف الأسنان",210,20,"Baby ready for first toothbrush","baby toothbrush toothpaste fluoride infant","Use fluoride-free paste under 2 years."),
    ("MS-019","First Shoes","أول حذاء",330,20,"Baby ready for first proper shoes","baby first shoes soft sole walking infant","Measure feet before buying."),
    ("MS-020","Swimwear / Pool Stage","مرحلة المسبح وملابس السباحة",365,30,"Child ready for water play","baby swimwear float arm bands pool toddler","Constant supervision near water."),
    ("MS-021","First Birthday Party Prep","التحضير لعيد الميلاد الأول",335,20,"Child approaching first birthday","birthday party supplies baby cake outfit","Avoid choking hazards in decorations."),
    ("MS-022","Pre-School Readiness","الاستعداد لما قبل المدرسة",1095,30,"Child approaching pre-school age","preschool bag stationery lunch box toddler","Ensure child's name on all items."),
    ("MS-023","Reading Readiness / First Books","الاستعداد للقراءة",548,30,"Child ready for picture books","baby books board book toddler reading","Board books for durability."),
    ("MS-024","Weaning from Bottle","الفطام من الرضاعة",365,30,"Baby ready to stop bottle feeding","sippy cup open cup training bottle weaning","Gradual transition recommended."),
    ("MS-025","Pregnancy — Third Trimester Hospital Bag","حقيبة المستشفى للثلث الثالث",245,30,"Mother in third trimester preparing hospital bag","hospital bag maternity newborn essentials labor","Pack 4-6 weeks before due date."),
]

rules = []
for m in MILESTONES:
    rules.append({
        "rule_id": m[0], "name_en": m[1], "name_ar": m[2],
        "typical_age_days": m[3], "window_days": m[4],
        "description": m[5], "search_query": m[6], "safety_note": m[7]
    })

os.makedirs("data", exist_ok=True)
with open("data/milestone_rules.json", "w", encoding="utf-8") as f:
    json.dump(rules, f, ensure_ascii=False, indent=2)

print(f"Generated {len(rules)} milestone rules -> data/milestone_rules.json")

# ── CATALOG — 50 products ──────────────────────────────────────────
CATALOG = [
  # (id, name_en, name_ar, category, [milestone_tags], age_min, age_max, price, [safety_certs], [incompatible_with], description_en, in_stock)
  # Feeding/weaning (8)
  ("MW-001","Chicco First Foods Weaning Set","طقم الفطام الأول من شيكو","feeding",["MS-001","MS-009"],4,12,89.0,["BPA-free","EN14350"],[],
   "Complete weaning starter kit with BPA-free bowls, soft-tip spoon, and silicone bib. Designed for babies beginning solid foods at 4-6 months.",True),
  ("MW-002","Philips Avent Silicone Feeding Spoons","ملاعق التغذية السيليكون من فيليبس أفنت","feeding",["MS-001"],4,12,45.0,["BPA-free"],[],
   "Set of 6 soft silicone weaning spoons in staged sizes. Heat-sensing tip alerts if food is too hot for baby.",True),
  ("MW-003","NUK First Choice Weaning Bowl Set","طقم أوعية الفطام من نوك","feeding",["MS-001"],4,18,65.0,["BPA-free"],[],
   "4-piece stackable weaning bowl set with anti-slip base and airtight lids. Dishwasher safe and microwave compatible.",True),
  ("MW-004","Munchkin Stay-Put Suction Bowls","أوعية المص الثابتة من مانشكين","feeding",["MS-001","MS-009"],6,24,55.0,["BPA-free"],[],
   "Toddler suction bowls that grip any smooth surface. Ideal for self-feeding babies aged 6 months and up.",True),
  ("MW-005","Chicco Easy Meal High Chair","كرسي الأكل إيزي ميل من شيكو","feeding",["MS-001"],6,36,349.0,["EN14988"],[],
   "Adjustable high chair with 7 height positions and 3-position reclining backrest. Easy-clean removable tray.",True),
  ("MW-006","MAM Silicone Trainer Sippy Cup","كوب التدريب السيليكوني من ماما","feeding",["MS-009"],6,18,49.0,["BPA-free"],[],
   "Leak-proof trainer cup with soft silicone spout and easy-grip handles. Transitions baby from bottle to cup.",True),
  ("MW-007","Pigeon Baby Food Maker Blender","خلاط طعام الأطفال من بيجون","feeding",["MS-001"],4,24,129.0,["BPA-free"],[],
   "All-in-one baby food maker that steams and blends in one bowl. Compact design for UAE kitchen counter.",True),
  ("MW-008","Dr Brown's Anti-Colic Bottle Set","طقم زجاجات مضادة للمغص من دكتور براون","feeding",["MS-006"],0,12,185.0,["BPA-free","EN14350"],[],
   "Set of 6 anti-colic bottles with internal vent system that reduces colic, gas, and spit-up. Newborn-safe nipple flow.",True),
  # Car seats (6)
  ("MW-009","Chicco KeyFit 30 Infant Car Seat","مقعد سيارة للرضع كي فيت 30 من شيكو","car_seats",["MS-005","MS-008"],0,12,699.0,["ECE R44/04"],["MW-010"],
   "Rear-facing infant car seat for newborns up to 13kg. One-second LATCH install system and EPS energy-absorbing foam.",True),
  ("MW-010","Graco 4Ever DLX Forward-Facing Car Seat","مقعد سيارة أمامي 4 في 1 من جريكو","car_seats",["MS-008"],9,144,1299.0,["ECE R129"],["MW-009"],
   "4-in-1 convertible car seat grows from infant to booster (4-45kg). Forward-facing from 9kg. Steel-reinforced frame.",True),
  ("MW-011","Joie i-Spin 360 Rotatable Car Seat","مقعد سيارة دوار 360 من جوي","car_seats",["MS-008"],0,48,1599.0,["ECE R129"],[],
   "Group 0+/1/2 car seat with 360-degree rotation for easy loading. Rear and forward facing. Fits from birth to 25kg.",True),
  ("MW-012","Britax Römer Baby-Safe 5Z2","مقعد سيارة بيبي سيف من بريتاكس","car_seats",["MS-005"],0,15,1899.0,["ECE R129"],[],
   "Rear-facing infant carrier certified for newborns to 15 months. Foldable ZipFix base and anti-rebound bar.",True),
  ("MW-013","Maxi-Cosi Pebble 360 Pro","مقعد سيارة بيبل 360 برو من ماكسي كوزي","car_seats",["MS-005"],0,15,2199.0,["ECE R129"],[],
   "Premium 360-degree infant car seat with one-hand rotation. I-Size safety certified. Fits Maxi-Cosi bases.",True),
  ("MW-014","Chicco Seat3Fit Forward-Facing","مقعد Seat3Fit للأمام من شيكو","car_seats",["MS-008"],9,144,999.0,["ECE R44/04"],[],
   "Convertible car seat from 9 to 36kg. Grows with child from toddler to school age. Side protection and ISOFIX.",True),
  # Strollers (5)
  ("MW-015","Silver Cross Wave Newborn Stroller","عربة الأطفال ويف من سيلفر كروس","strollers",["MS-017"],0,36,3499.0,["EN1888"],[],
   "Premium all-terrain stroller with reversible seat and carrycot option. Suitable from birth to 25kg.",True),
  ("MW-016","Bugaboo Bee6 Compact Stroller","عربة بي 6 المدمجة من بوقابو","strollers",["MS-017"],6,48,2999.0,["EN1888"],[],
   "Lightweight urban stroller folds in one move. Reversible seat, large sun canopy, and puncture-proof tires.",True),
  ("MW-017","Maclaren Techno XT Umbrella Stroller","عربة تكنو إكس تي المظلة من ماكلارين","strollers",["MS-017"],6,48,999.0,["EN1888"],[],
   "Lightweight aluminium umbrella stroller for urban parents. Folds in seconds, padded seat, UV50+ canopy.",True),
  ("MW-018","Joie Versatrax Pushchair","عربة ڤيرساتراكس من جوي","strollers",["MS-017"],0,36,1599.0,["EN1888"],[],
   "Modular pushchair with 3 seat configurations. Compact fold, extended canopy, and all-terrain wheels.",True),
  ("MW-019","Baby Jogger City Mini GT2","عربة سيتي ميني GT2 من بيبي جوجر","strollers",["MS-017"],0,36,1899.0,["EN1888"],[],
   "Single-hand quick-fold stroller with all-terrain rubber tires. Suitable from birth with lie-flat seat.",True),
  # Sleep/cribs/bassinets (5)
  ("MW-020","SNOO Smart Bassinet","مهد ذكي سنو","sleep",["MS-005","MS-006"],0,6,3999.0,["ASTM F2194"],["MW-021"],
   "Responsive bassinet that automatically soothes crying babies with gentle motion and white noise. App-controlled.",True),
  ("MW-021","Chicco Next2Me Forever Bedside Crib","سرير جانبي نيكست تو مي من شيكو","sleep",["MS-005"],0,9,1199.0,["EN1130"],["MW-020"],
   "Co-sleeper that attaches securely to parents' bed. Adjusts to 11 heights. Converts to standalone crib.",True),
  ("MW-022","Stokke Sleepi Convertible Crib","سرير قابل للتحويل سليبي من ستوكي","sleep",["MS-005","MS-013"],0,60,2499.0,["EN716"],[],
   "Oval crib converts from bassinet to crib to junior bed. Grows from birth to age 5. Sustainably sourced wood.",True),
  ("MW-023","Bubba Blue Breathe-Eze Crib Mattress","مرتبة سرير قابلة للتنفس من بوبا بلو","sleep",["MS-005","MS-013"],0,36,299.0,["OEKO-TEX"],[],
   "Open-cell foam crib mattress with breathable mesh cover. Temperature-regulating and hypoallergenic.",True),
  ("MW-024","Aden + Anais Dream Muslin Blanket","بطانية موسلين ادن وأناس","sleep",["MS-006"],0,24,149.0,["OEKO-TEX"],[],
   "100% cotton muslin swaddle blanket. Breathable, softens with every wash. Ideal for UAE warm climate.",True),
  # Bath/grooming (5)
  ("MW-025","Summer Infant Newborn-to-Toddler Bath Tub","حوض استحمام من سامر إنفانت","bath",["MS-011"],0,24,159.0,["ASTM F2670"],[],
   "Convertible bath tub with sling insert for newborns and seat for toddlers. Non-slip base and drain plug.",True),
  ("MW-026","Stokke Flexi Bath Foldable Baby Tub","حوض استحمام قابل للطي من ستوكي","bath",["MS-011"],0,48,249.0,[],[],
   "Collapsible bath tub that folds flat for storage and travel. Ergonomic newborn insert sold separately.",True),
  ("MW-027","Angelcare Baby Bath Seat Ring","كرسي حمام الأطفال من أنجيلكير","bath",["MS-011"],6,18,179.0,["EN17022"],[],
   "Soft mesh bath seat with suction feet for stability. Supports sitting baby safely. Easy to fold and store.",True),
  ("MW-028","Johnson's Baby Skincare Gift Set","طقم العناية بالبشرة من جونسون","bath",["MS-011"],0,12,89.0,[],[],
   "Complete baby skincare set: gentle shampoo, lotion, baby wash, and oil. Clinically tested, tear-free formula.",True),
  ("MW-029","Babymoov Aquadots Bath Seat","كرسي الاستحمام أكوادوتس من بيبيموف","bath",["MS-011"],6,18,199.0,[],[],
   "Inflatable bath seat with 6 suction cups for stability. Folds flat. BPA-free PVC, easy to clean.",True),
  # Toys/development (8)
  ("MW-030","Fisher-Price Tummy Time Play Mat","حصيرة وقت البطن من فيشر برايس","toys",["MS-002","MS-003"],0,6,199.0,["ASTM F963"],[],
   "Cushioned play mat with high-contrast patterns and hanging toys to encourage tummy time and early development.",True),
  ("MW-031","Skip Hop Explore & More Baby Walker","ووكر الاستكشاف من سكيب هوب","toys",["MS-004"],9,36,389.0,["ASTM F977"],[],
   "3-stage activity walker with removable activity station. Non-slip rubber tips and height-adjustable frame.",True),
  ("MW-032","VTech Sit-to-Stand Learning Walker","ووكر التعلم من في تيك","toys",["MS-004"],9,36,299.0,["EN71"],[],
   "Interactive learning walker with piano keys, shape sorter, and educational songs. Grows from seated play to walking.",True),
  ("MW-033","Melissa & Doug Wooden Activity Set","طقم ألعاب خشبية من ميليسا وداوج","toys",["MS-016","MS-022"],36,72,249.0,["EN71","ASTM F963"],[],
   "10-piece wooden activity set with bead maze, shape puzzle, and peg board. Non-toxic paint. Develops fine motor skills.",True),
  ("MW-034","Baby Einstein Sensory Discovery Kit","مجموعة الاستكشاف الحسي من بيبي آينشتاين","toys",["MS-002","MS-003"],0,12,189.0,["EN71"],[],
   "Multi-sensory play kit with crinkle cards, teether, and activity book. Stimulates vision and touch from birth.",True),
  ("MW-035","Nuby Bounce n Play Activity Ball","كرة النشاط من نوبي","toys",["MS-003","MS-004"],6,24,99.0,["BPA-free","EN71"],[],
   "Textured sensory ball that encourages crawling and walking. Rattle sounds inside, easy-grip bumps on surface.",True),
  ("MW-036","LEGO DUPLO Classic Brick Box","صندوق مكعبات ليجو دوبلو","toys",["MS-016"],24,60,199.0,["EN71"],[],
   "65-piece DUPLO brick set for creative building play. Large bricks safe for toddlers. Develops spatial reasoning.",True),
  ("MW-037","Tiny Love 3-in-1 Rocker Napper","مهدة ومرجوحة 3 في 1 من تيني لوف","toys",["MS-002"],0,9,899.0,["ASTM F2194"],[],
   "Convertible rocker, napper, and stationary seat. Vibration and music modes. Folds flat for storage or travel.",True),
  # Clothing/shoes (4)
  ("MW-038","Stride Rite Baby's First Walkers","أول أحذية المشي من سترايد رايت","shoes",["MS-004","MS-019"],6,24,189.0,[],[],
   "Soft leather first-step shoes with wide toe box and flexible sole. Machine washable. Supports natural foot development.",True),
  ("MW-039","Clarks Baby Softly Dreamz First Shoes","أول أحذية من كلاركس","shoes",["MS-019"],9,18,219.0,[],[],
   "Leather pre-walking shoes with extra-soft sole for early walkers. Breathable lining and easy velcro fastening.",True),
  ("MW-040","Carter's Baby Essential Wardrobe Set","طقم ملابس أساسية من كارترز","clothing",["MS-007"],0,24,299.0,["OEKO-TEX"],[],
   "10-piece essential wardrobe set: bodysuits, sleepers, and pants. 100% cotton, snap closures for easy dressing.",True),
  ("MW-041","Purebaby Organic Cotton Onesie 5-Pack","طقم 5 أوزة أورجانيك من بيوربيبي","clothing",["MS-007"],0,12,149.0,["GOTS","OEKO-TEX"],[],
   "GOTS certified organic cotton onesies. Envelope neckline for easy dressing. Tagless for sensitive skin.",True),
  # Nursery/school bags (4)
  ("MW-042","Skip Hop Zoo Mini Backpack","حقيبة ظهر ميني حديقة الحيوان","bags",["MS-007","MS-014"],12,48,119.0,[],[],
   "Toddler backpack with padded back panel and chest clip. 3L capacity, animal character designs, easy-clean lining.",True),
  ("MW-043","JuJuBe Be Prepared Diaper Bag","حقيبة حفاضات من جوجوبي","bags",["MS-007"],0,36,549.0,[],[],
   "Large diaper backpack with 18 pockets and stroller clips. Machine washable lining, insulated bottle pockets.",True),
  ("MW-044","Pottery Barn Kids Classic Backpack","حقيبة ظهر كلاسيك للأطفال","bags",["MS-014","MS-022"],24,72,299.0,[],[],
   "Durable canvas backpack for nursery and pre-school. Monogrammable, padded straps, and wipeable lining.",True),
  ("MW-045","OiOi Vegan Leather Nappy Bag","حقيبة حفاضات جلد نباتي من أوي أوي","bags",["MS-007"],0,36,449.0,[],[],
   "Stylish vegan leather nappy bag with 12 internal pockets, changing mat, and insulated bottle holder.",True),
  # Health/teething (5)
  ("MW-046","Sophie La Girafe Teething Toy","لعبة التسنين سوفي الزرافة","health",["MS-010"],3,18,129.0,["EN71","LFGB"],[],
   "Classic natural rubber teething toy. Multiple textures to soothe sore gums. 100% natural rubber and food-grade paint.",True),
  ("MW-047","NUK Genius Silicone Teether Set","طقم مضغاط السيليكون الجينيوس من نوك","health",["MS-010"],3,18,89.0,["BPA-free","EN71"],[],
   "3-piece silicone teether set in different textures. Fridge-safe to soothe inflamed gums. Easy-grip design.",True),
  ("MW-048","Brush-Baby Chewable Toothbrush Set","طقم فرشاة أسنان قابلة للمضغ من براش بيبي","health",["MS-010","MS-018"],0,18,79.0,["BPA-free"],[],
   "Silicone finger toothbrush doubles as teether. Introduces gum massage and oral hygiene from 0 months.",True),
  ("MW-049","CURAPROX Baby Toothbrush Set","طقم فرشاة أسنان من كيوراوبروكس","health",["MS-018"],0,36,65.0,[],[],
   "Ultra-soft 12,000-filament baby toothbrush with ergonomic handle. Ideal for introducing tooth brushing at 7 months.",True),
  ("MW-050","NoseFrida SnotSucker + Gripe Water Bundle","حزمة NoseFrida ومياه الكمون","health",["MS-006"],0,12,119.0,[],[],
   "Nasal aspirator with 20 hygienic filters plus gripe water for gas relief. Essential newborn health bundle.",True),
]

catalog = []
for c in CATALOG:
    catalog.append({
        "product_id": c[0], "name_en": c[1], "name_ar": c[2],
        "category": c[3], "milestone_tags": c[4],
        "age_min_months": c[5], "age_max_months": c[6],
        "price_aed": c[7], "safety_certs": c[8],
        "incompatible_with": c[9], "description_en": c[10], "in_stock": c[11]
    })

with open("data/catalog.json", "w", encoding="utf-8") as f:
    json.dump(catalog, f, ensure_ascii=False, indent=2)
print(f"Generated {len(catalog)} products -> data/catalog.json")

# ── CUSTOMERS — 20 profiles ────────────────────────────────────────
from datetime import date, timedelta
today = date.today()
def dob(days_ago): return (today - timedelta(days=days_ago)).isoformat()

CUSTOMERS = [
  # (id, name, language, child_dob, purchase_history, country, note)
  # Easy notify cases
  ("C-001","Fatima Al-Rashid","ar",dob(175),["MW-043"],"UAE",""),         # MS-001 Starting Solids in 5d
  ("C-002","Sara Mitchell","en",dob(358),["MW-015"],"UAE",""),            # MS-004 First Steps in 7d
  ("C-003","Nour Al-Ahmad","ar",dob(143),["MW-024"],"KSA",""),            # MS-010 Teething in 7d
  ("C-004","Hessa Al-Mansouri","ar",dob(83),["MW-028"],"UAE",""),         # MS-002 Tummy Time in 7d
  ("C-005","Emma Thompson","en",dob(325),["MW-009","MW-040"],"UAE",""),   # MS-021 First Birthday in 10d
  # Silent cases
  ("C-006","Maryam Al-Zaabi","ar",dob(531),["MW-022"],"KSA",""),          # MS-012 Potty Training in 9d -> notify
  ("C-007","Jessica Williams","en",dob(500),["MW-017"],"UAE",""),         # dead zone, silent
  ("C-008","Aisha Al-Blooshi","ar",dob(203),["MW-028"],"Kuwait",""),      # MS-018 Toothbrushing in 7d
  ("C-009","Chloe Davidson","en",dob(1),[],"UAE",""),                     # newborn, silent
  ("C-010","Shaikha Al-Nuaimi","ar",dob(723),["MW-042"],"KSA",""),       # MS-015 Outdoor in 7d
  ("C-011","Rachel Green","en",dob(50),[],"UAE",""),                      # between milestones, silent
  # Adversarial
  ("C-012","Noura Al-Rashidi","ar",dob(175),["MW-001","MW-002","MW-003","MW-004","MW-005","MW-006","MW-007"],"UAE","all feeding owned"),  # MS-001 but all products owned
  ("C-013","Amy Johnson","en",dob(537),["MW-036"],"KSA",""),              # MS-012 in 3d, confidence boundary
  ("C-014","Reem Al-Maktoum","ar",dob(80),["MW-037"],"UAE",""),           # MS-002 and MS-005 both at 90d window
  ("C-015","Mariam Al-Suwaidi","ar",None,[],"KSA","pregnant"),            # pregnant, no DOB -> silent
  ("C-016","Olivia Brown","en",dob(264),["MW-040"],"Kuwait",""),          # MS-007 Day Care in 6d
  ("C-017","Sarah Collins","en",dob(545),["MW-017"],"UAE",""),            # MS-017 Stroller->Walking in 3d
  # No DOB (new accounts)
  ("C-018","Sophie Anderson","en",None,[],"UAE","new account"),
  ("C-019","Khalood Al-Shamsi","ar",None,[],"KSA","new account"),
  # 14-year-old (aged out)
  ("C-020","Linda Carson","en",dob(14*365),["MW-010"],"UAE","14yo aged out"),
]

customers = []
for c in CUSTOMERS:
    entry = {
        "customer_id": c[0], "name": c[1], "language": c[2],
        "child_dob": c[3], "purchase_history": c[4], "country": c[5]
    }
    if c[6]: entry["note"] = c[6]
    customers.append(entry)

with open("data/customers.json", "w", encoding="utf-8") as f:
    json.dump(customers, f, ensure_ascii=False, indent=2)
print(f"Generated {len(customers)} customers -> data/customers.json")
