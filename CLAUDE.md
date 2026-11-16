# Kidmat Yafo — company website

Static one-page site for Kidmat Yafo Megurim (קידמת יפו מגורים). Hebrew, right-to-left, one fluid page for desktop and phone.
Sister site of Bilu 10 (repo `bilu10`, live at https://bilu10.com). Main domain: kidmatyafo.co.il (the company's established address; DNS at SPD hosting, pointed to Vercel on 12 Nov 2026). kidmatyafo.com (GoDaddy) is a second address for the same site. Do not touch DNS without Amir.

## Where the design comes from
The design is made in a claude.ai canvas ("קידמת יפו — סקיצת אתר חדש").
- `src/Main.dc.html` — the home page, exported from the canvas desktop board (the page is fluid; there is no separate phone file)
- `assets/` — every image, plus `assets/blobs.json`, which maps canvas image ids (`/_blob/<id>`) to file names
- `build.py` turns these into `dist/` (index.html, img/, sitemap.xml, robots.txt) and adds the page title, description,
  share image, structured data, the contact-form sender and the menu behaviour.

## Rules Amir set
- Don't change texts or structure without asking.
- No "תמ״א 38" wording (use "חיזוק ותוספת"); don't present the company as the executing contractor.
- Contact-form enquiries go to hadadbox@gmail.com (formsubmit.co).
- SEO priority: searching "קידמת יפו" should bring up this site; "בילו 10" should bring up bilu10.com.

## Syncing a canvas change
1. Replace `src/Main.dc.html` with the canvas board file; add any new image to `assets/` and its id to `assets/blobs.json`.
2. Run `python3 build.py` — it must finish without "Missing image".
3. Check `dist/index.html` at 1440 wide and at 390 wide.
4. Commit and push to `main`.

## The Tchernichovsky 10 penthouse landing page
`/penthouse` is an English landing page for the penthouse at Tchernichovsky 10, with its live 3D plan (`/penthouse/3d`) embedded.
Both are prebuilt files in `penthouse/` (`index.html`, `3d.html`); `build.py` only copies the folder into `dist/`. The page uses
`/img/proj-tchernichovsky.jpg`, which the home page already ships. It was added in code, not in the canvas. The pages carry `noindex`
until Amir approves the texts.
