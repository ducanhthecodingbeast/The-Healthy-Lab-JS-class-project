import os

with open("index.html", "r") as f:
    lines = f.readlines()

head_part = lines[:46]
head_part.insert(45, '  <link rel="stylesheet" href="./assets/css/journal-post.css">\n')

header_part = lines[46:117]
footer_part = lines[997:] # From <!-- - #FOOTER -->

def write_journal(filename, title, meta, badge, img_src, content_html):
    html = "".join(head_part)
    html += "".join(header_part)
    html += '  <main>\n    <article class="journal-post">\n'
    
    html += f'''
      <header class="journal-header">
        <span class="journal-badge">{badge}</span>
        <h1 class="journal-title">{title}</h1>
        <div class="journal-meta">
          {meta}
        </div>
      </header>

      <img src="{img_src}" alt="{title}" class="journal-hero-img">

      <div class="journal-content">
        {content_html}
        
        <div class="journal-back">
          <a href="index.html#blog">
            <ion-icon name="arrow-back"></ion-icon>
            Back to Journal
          </a>
        </div>
      </div>
    '''

    html += '    </article>\n  </main>\n'
    html += "".join(footer_part)
    
    with open(filename, "w") as f:
        f.write(html)

j1_title = "5 Morning Rituals That Actually Change Your Energy"
j1_meta = '<div class="journal-meta-item"><ion-icon name="calendar-outline"></ion-icon> <time datetime="2025-03-12">Mar 12 2025</time></div> <div class="journal-meta-item"><ion-icon name="person-outline"></ion-icon> <span>Dr. Linh Tran</span></div>'
j1_badge = "Wellness"
j1_img = "./assets/images/blog-1.png"
j1_content = '''
<p>From hydration timing to mindful movement, small habits compound into lasting vitality. Building a strong morning routine isn't about waking up at 4 AM and running a marathon; it's about intentional actions that signal to your body that the day has begun.</p>
<h2>1. The Lemon Water Wake-Up</h2>
<p>Before coffee, rehydrate. After 7-8 hours of sleep, your body is naturally dehydrated. A large glass of room temperature water with a squeeze of fresh lemon jumpstarts digestion and flushes toxins.</p>
<h2>2. Five Minutes of Sunlight</h2>
<p>Getting natural light in your eyes within 30 minutes of waking sets your circadian rhythm, suppressing melatonin and boosting cortisol naturally so you feel alert without the jitters.</p>
<blockquote>"How you spend your first hour sets the tone for your entire day."</blockquote>
<h2>3. Delay Caffeine</h2>
<p>Wait at least 90 minutes after waking before your first cup of coffee. This allows your body's natural cortisol peak to clear adenosine (the sleepiness chemical), preventing the dreaded afternoon crash.</p>
<h2>4. High-Protein Breakfast</h2>
<p>Skip the pastries. Aim for 30 grams of protein to stabilize blood sugar. Our Nourish Bowls are perfect for this.</p>
<h2>5. Mindful Movement</h2>
<p>You don't need a heavy workout. Just 10 minutes of stretching or walking gets the blood flowing and clears brain fog.</p>
'''

write_journal("journal-1.html", j1_title, j1_meta, j1_badge, j1_img, j1_content)

j2_title = "The Power of Fermented Foods for Gut Health"
j2_meta = '<div class="journal-meta-item"><ion-icon name="calendar-outline"></ion-icon> <time datetime="2025-04-01">Apr 01 2025</time></div> <div class="journal-meta-item"><ion-icon name="person-outline"></ion-icon> <span>Chef Minh Dao</span></div>'
j2_badge = "Nutrition"
j2_img = "./assets/images/blog-2.png"
j2_content = '''
<p>Kimchi, kefir, miso — discover how ancient preservation unlocks your microbiome's potential. Fermentation isn't just a culinary trend; it's a foundational pillar of human nutrition that we've largely lost in the modern diet.</p>
<h2>What is Fermentation?</h2>
<p>Fermentation is a metabolic process where microorganisms (like bacteria and yeast) break down carbohydrates into organic acids or alcohol. In foods like yogurt, sauerkraut, and kombucha, this process creates probiotics.</p>
<h2>Why Your Gut Needs It</h2>
<ul>
  <li><strong>Enhanced Digestion:</strong> Fermented foods are partially broken down before you even eat them.</li>
  <li><strong>Nutrient Absorption:</strong> The fermentation process increases the bioavailability of vitamins, particularly B vitamins and vitamin K.</li>
  <li><strong>Immune Support:</strong> 70% of your immune system resides in your gut. A diverse microbiome is a strong microbiome.</li>
</ul>
<blockquote>"Fermentation is culinary alchemy that transforms ordinary ingredients into superfoods."</blockquote>
<h2>How to Incorporate Them Daily</h2>
<p>Start small. Add a forkful of raw sauerkraut to your salad, swap regular yogurt for kefir, or use miso paste in your salad dressings. At The Healthy Lab, we feature house-fermented pickles and kombucha on tap to make it easy to get your daily dose.</p>
'''

write_journal("journal-2.html", j2_title, j2_meta, j2_badge, j2_img, j2_content)

j3_title = "Building a Nourish Bowl: The Art of Balanced Eating"
j3_meta = '<div class="journal-meta-item"><ion-icon name="calendar-outline"></ion-icon> <time datetime="2025-04-18">Apr 18 2025</time></div> <div class="journal-meta-item"><ion-icon name="person-outline"></ion-icon> <span>Hana Nguyen, RD</span></div>'
j3_badge = "Recipes"
j3_img = "./assets/images/blog-3.png"
j3_content = '''
<p>Grains, proteins, healthy fats and colour — a step-by-step guide to the perfect bowl. The beauty of a bowl meal lies in its versatility. It's the perfect vehicle for combining macronutrients in a way that is both visually appealing and deeply satisfying.</p>
<h2>Step 1: The Base (30%)</h2>
<p>Start with a complex carbohydrate. Quinoa, brown rice, farro, or sweet potato noodles provide sustained energy. If you're looking for a lighter option, use a bed of dark leafy greens like kale or spinach.</p>
<h2>Step 2: The Protein (25%)</h2>
<p>This keeps you full. Grilled salmon, baked tofu, edamame, or roasted chickpeas. Aim for a portion about the size of your palm.</p>
<h2>Step 3: The Color (30%)</h2>
<p>Eat the rainbow. Roasted beets, shredded carrots, cherry tomatoes, purple cabbage, and blanched broccoli. Different colors represent different phytonutrients.</p>
<blockquote>"A balanced bowl isn't a restriction; it's an abundance of nutrients."</blockquote>
<h2>Step 4: Healthy Fats & Crunch (10%)</h2>
<p>Avocado, toasted pumpkin seeds, hemp hearts, or walnuts. Fats are essential for absorbing fat-soluble vitamins (A, D, E, and K) from your vegetables.</p>
<h2>Step 5: The Dressing (5%)</h2>
<p>Tie it all together. A lemon-tahini drizzle, ginger-miso vinaigrette, or simple olive oil and balsamic. Keep it light and vibrant.</p>
'''

write_journal("journal-3.html", j3_title, j3_meta, j3_badge, j3_img, j3_content)

print("Files created successfully!")
