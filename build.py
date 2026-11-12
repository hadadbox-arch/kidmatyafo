#!/usr/bin/env python3
"""Build the Kidmat Yafo company site from the canvas screen.

src/Main.dc.html   -> exported from the claude.ai canvas (edit there, then sync)
assets/blobs.json  -> maps canvas image ids (/_blob/<id>) to files in assets/
Output: dist/index.html, dist/img/*, dist/sitemap.xml, dist/robots.txt
"""
import re, os, json, shutil
ROOT = os.path.dirname(os.path.abspath(__file__))
SRC, ASSETS, OUT = (os.path.join(ROOT, d) for d in ('src', 'assets', 'dist'))
BLOB = json.load(open(os.path.join(ASSETS, 'blobs.json')))

SITE = 'https://kidmatyafo.co.il'
INBOX = 'hadadbox@gmail.com'   # enquiries from the contact form are emailed here (via formsubmit.co)
TITLE = 'קידמת יפו מגורים | מגורים והתחדשות עירונית בתל אביב'
DESC = ('קידמת יפו מגורים יוזמת ובונה פרויקטים למגורים ולהתחדשות עירונית בתל אביב וביפו. '
        'הפרויקט המוביל: ביל״ו 10 (בילו 10) בלב העיר הלבנה.')
PHONE, EMAIL, STREET = '+972529777200', 'yafo38@gmail.com', 'זמנהוף 3'

ORG = {
    '@context': 'https://schema.org', '@type': 'RealEstateAgent', '@id': SITE + '/#org',
    'name': 'קידמת יפו מגורים', 'alternateName': ['קידמת יפו', 'Kidmat Yafo', 'Kidmat Yafo Megurim'],
    'url': SITE + '/', 'logo': SITE + '/img/kidmat-logo.png', 'image': SITE + '/img/hero-building.jpg',
    'description': DESC, 'telephone': PHONE, 'email': EMAIL,
    'address': {'@type': 'PostalAddress', 'streetAddress': STREET, 'addressLocality': 'תל אביב-יפו', 'addressCountry': 'IL'},
    'areaServed': ['תל אביב-יפו', 'רמת גן'],
    'subjectOf': {'@type': 'WebSite', 'name': 'BILU 10 · ביל״ו 10', 'url': 'https://bilu10.com/'},
}

JS = r"""
(function(){
  var d=document;
  // close the menu after choosing a link, or when clicking outside it
  var menu=d.querySelector('.ky-menu');
  if(menu){
    menu.addEventListener('click',function(e){if(e.target.closest('nav a'))menu.removeAttribute('open');});
    d.addEventListener('click',function(e){if(menu.hasAttribute('open')&&!menu.contains(e.target))menu.removeAttribute('open');});
  }
  // contact form
  var btn=d.querySelector('#contact button[type=button]');
  if(!btn)return;
  function el(id){return d.getElementById(id);}
  function val(id){var e=el(id);return e?(e.value||'').trim():'';}
  btn.addEventListener('click',function(){
    var name=val('ky-name'),phone=val('ky-phone'),mail=val('ky-mail');
    var t=el('ky-topic'),topic=t&&t.options?t.options[t.selectedIndex].text:'';
    var bad=[];
    if(!name)bad.push(el('ky-name'));
    if(!phone&&!mail)bad.push(el('ky-phone'));
    ['ky-name','ky-phone'].forEach(function(id){var e=el(id);if(e){e.style.borderColor='#3C3429';e.style.borderWidth='1px';}});
    if(bad.length){bad.forEach(function(e){if(e){e.style.borderColor='#B3261E';e.style.borderWidth='2px';}});if(bad[0])bad[0].focus();return;}
    btn.disabled=true;
    try{fetch('https://formsubmit.co/ajax/__INBOX__',{method:'POST',headers:{'Content-Type':'application/json','Accept':'application/json'},
      body:JSON.stringify({_subject:'פנייה מאתר קידמת יפו: '+topic,_template:'table',_captcha:'false','נושא':topic,'שם':name,'טלפון':phone,'דוא״ל':mail,'עמוד':location.href})});}catch(e){}
    var box=btn.parentNode;
    box.innerHTML='<p role="status" style="margin:0;font-size:24px;line-height:1.4;font-weight:300">תודה, '+name.replace(/[<>&]/g,'')+'.<br>קיבלנו את הפנייה ונחזור אליכם בהקדם.</p>';
  });
})();
""".replace('__INBOX__', INBOX)

CSS = """
html{scroll-behavior:smooth;scroll-padding-top:92px}
img{max-width:100%}
a:focus-visible,button:focus-visible,summary:focus-visible,input:focus-visible,select:focus-visible{outline:2px solid #4D4A86;outline-offset:3px}
@media (max-width:600px){.ky-plus{flex-basis:36px!important;width:36px!important;height:36px!important;font-size:24px!important}.ky-sum>div{padding-top:22px!important;padding-bottom:22px!important}}
@media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
"""

def build():
    shutil.rmtree(OUT, ignore_errors=True)
    os.makedirs(os.path.join(OUT, 'img'))
    s = open(os.path.join(SRC, 'Main.dc.html'), encoding='utf-8').read()
    for b in set(re.findall(r'/_blob/([0-9a-f]{32})', s)):
        if b not in BLOB:
            raise SystemExit(f'Missing image for /_blob/{b}: add the file to assets/ and its id to assets/blobs.json')
        shutil.copy(os.path.join(ASSETS, BLOB[b]), os.path.join(OUT, 'img', BLOB[b]))
        s = s.replace('/_blob/' + b, 'img/' + BLOB[b])
    for f in ('favicon-48.png', 'favicon-192.png'):  # square site icons (search engines need a square one)
        shutil.copy(os.path.join(ASSETS, f), os.path.join(OUT, 'img', f))
    helmet = re.search(r'<helmet>(.*?)</helmet>', s, re.S).group(1).strip()
    body = re.search(r'</helmet>(.*?)</x-dc>', s, re.S).group(1).strip()
    helmet = helmet.replace('</style>', CSS + '</style>')
    # every image below the opening screen loads lazily
    first = [True]
    def lazy(m):
        tag = m.group(0)
        if 'hero-building' in tag or 'kidmat-logo' in tag:
            return tag.replace('<img ', '<img decoding="async" ')
        return tag.replace('<img ', '<img loading="lazy" decoding="async" ')
    body = re.sub(r'<img [^>]*>', lazy, body)
    head = f'''<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{TITLE}</title>
<meta name="description" content="{DESC}">
<link rel="canonical" href="{SITE}/">
<meta name="theme-color" content="#F0EDE4">
<link rel="icon" type="image/png" sizes="48x48" href="/img/favicon-48.png">
<link rel="icon" type="image/png" sizes="192x192" href="/img/favicon-192.png">
<link rel="apple-touch-icon" href="/img/favicon-192.png">
<meta property="og:type" content="website">
<meta property="og:locale" content="he_IL">
<meta property="og:site_name" content="קידמת יפו מגורים">
<meta property="og:title" content="{TITLE}">
<meta property="og:description" content="{DESC}">
<meta property="og:url" content="{SITE}/">
<meta property="og:image" content="{SITE}/img/hero-building.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preload" as="image" href="/img/hero-building.jpg">
{helmet}
<script type="application/ld+json">{json.dumps(ORG, ensure_ascii=False)}</script>'''
    html = f'<!doctype html>\n<html lang="he" dir="rtl">\n<head>\n{head}\n</head>\n<body>\n{body}\n<script>{JS}</script>\n</body>\n</html>\n'
    open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(html)
    open(os.path.join(OUT, 'robots.txt'), 'w').write(f'User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n')
    open(os.path.join(OUT, 'sitemap.xml'), 'w').write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f'  <url><loc>{SITE}/</loc></url>\n</urlset>\n')
    # Google Search Console ownership file for https://kidmatyafo.co.il (keep it, or the site loses its verification)
    open(os.path.join(OUT, 'google57f8a8dc096e3a3e.html'), 'w').write('google-site-verification: google57f8a8dc096e3a3e.html')
    print('built dist/: index.html', len(html) // 1024, 'KB,', len(os.listdir(os.path.join(OUT, 'img'))), 'images')

if __name__ == '__main__':
    build()
