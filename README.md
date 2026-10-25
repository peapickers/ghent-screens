# two-step

Film, theatre, dance, music, talks and exhibitions in and around Ghent (arthouse cinemas and film clubs such as Sphinx, Studio Skoop, KASKcinema and Ciné Rio), with a **Funding** article on who paid for each film. Kinepolis is not included.

This repository is the public site. GitHub Pages serves it for free at `https://peapickers.github.io/ghent-screens/`:

| File | What it is |
|---|---|
| `index.html` | The interactive page: filter by cinema, start time, kind of film, money type, studio or fund, country |
| `screenings.json` | All listed screenings |
| `films.json` | Film metadata and Funding articles, with sources |
| `feed.xml` | RSS feed, one item per day |
| `scripts/` | The free Python scripts that build the post, the feed and the film data |
| `igmcp/` | Files for the Instagram posting server on your Mac |

## Automatic updates

A GitHub Actions workflow (`.github/workflows/update-listings.yml`) runs every Wednesday morning, for free and without Claude:

1. `scripts/update_films.py` reads the official programme pages of Sphinx, Studio Skoop, KASKcinema and Ciné Rio. It keeps only facts (date, time, title, a short label, the link) and copies no images or descriptions.
2. `scripts/update_stage.py` does the same for theatre, dance and stage music: NTGent, VIERNULVIER, CAMPO, Kopergietery, Arca, Opera Ballet Vlaanderen (Ghent dates only), De Centrale, Theater Box and amateur theatre within 25 km of Gent (OPENDOEK). Arca and Opera Ballet load their calendars with JavaScript, so a free headless browser (Playwright) reads those two. VIERNULVIER and CAMPO ask for 5 seconds between requests; the script waits.
3. `scripts/build_feed.py` rebuilds `feed.xml`.
4. The workflow commits the changes and GitHub Pages republishes the site.

If a venue's page can't be read (for example after a site redesign), its last known listings stay and a notice on the site says so. To run it by hand: **Actions → Weekly listings update → Run workflow**.

Not automatic: Funding articles (new titles show "Funding: unknown" until a sourced article is added), talks and exhibitions. Those are updated in a Claude session.

Robots.txt of every venue allows these pages (checked 25-10-2026); none of their sites has terms that forbid automated reading.

Everything below is free. Steps 1–2 take about 5 minutes. Steps 3–5 take about 30 minutes, once.

## 1. Create the repository (GitHub)

1. Sign up or sign in at github.com (free).
2. Create a **public** repository named `ghent-screens`. Leave it empty: no README, no licence.
3. In Claude, connect GitHub (Settings → Connectors) and give it access to `ghent-screens`, then tell Claude "push the two-step site". Claude uploads these files.
4. In the repository, open **Settings → Pages**. Under *Build and deployment* pick **Deploy from a branch**, branch `main`, folder `/ (root)`, then **Save**. The site is live within a few minutes.
5. Tell Claude your GitHub username so the RSS feed gets the right address.

## 2. Instagram account (Instagram app, phone)

Instagram only lets software post to a **professional** account.

1. Profile → ☰ → **Account type and tools** → **Switch to professional account**. Choose **Creator** or **Business**, both free.
2. Create a **Facebook Page** (free) for the account and link it under Instagram **Settings → Accounts Center**. The Graph API needs this link.

## 3. Meta developer app (computer, developers.facebook.com)

1. Go to developers.facebook.com, log in with the Facebook account that owns the Page, and **Create app**. Choose the use case **Other**, then app type **Business**.
2. Add the **Instagram** product and choose **API setup with Facebook login**.
3. Open **Tools → Graph API Explorer**. Select your app, then **Get Token → Get User Access Token** with these permissions only:
   - `instagram_basic`
   - `instagram_content_publish`
   - `pages_show_list`
   - `pages_read_engagement`
   - `business_management`

   Don't add messaging permissions. The server is set up to post only.
4. Make it a 60-day token: open **Tools → Access Token Debugger**, paste the token, then click **Extend Access Token**.
5. Find your Instagram account ID by running this query in Graph API Explorer: `me/accounts?fields=instagram_business_account{id,username}`. Copy the `instagram_business_account.id`.
6. App ID and App Secret are under **App settings → Basic**.

Keep the token, app secret and account ID on your Mac only. Never paste them into a chat, a repository or a website.

## 4. Install ig-mcp on your Mac (Terminal)

ig-mcp is open source (MIT). Before you install it, I reviewed the code at commit `549fbee`:

- **Network:** it only talks to `graph.facebook.com` and `graph.instagram.com`. It also downloads the image you post, to check its shape.
- **Your token:** it stays in a local `.env` file.
- **Risky code:** none found. No shell commands, no calls to other servers.
- **Direct messages:** it includes a DM-sending tool. `add_carousel.py` removes it, and your token has no messaging permission either.

Install Python 3.12 from python.org (it supports macOS 12). Then run:

```bash
cd ~
git clone https://github.com/jlbadano/ig-mcp.git
cd ig-mcp
git checkout 549fbee                      # the version that was reviewed
curl -fsSLO https://peapickers.github.io/ghent-screens/igmcp/add_carousel.py
curl -fsSLO https://peapickers.github.io/ghent-screens/igmcp/run.sh
curl -fsSLO https://peapickers.github.io/ghent-screens/igmcp/requirements-slim.txt
python3 add_carousel.py                   # adds publish_carousel, removes send_dm
python3.12 -m venv .venv
.venv/bin/pip install -r requirements-slim.txt
chmod +x run.sh
cp env.example .env && open -e .env       # fill in the four values below, save
```

In `.env`, fill in:

```
FACEBOOK_APP_ID=...
FACEBOOK_APP_SECRET=...
INSTAGRAM_ACCESS_TOKEN=...          (the 60-day token)
INSTAGRAM_BUSINESS_ACCOUNT_ID=...
```

Test the setup:

```bash
.venv/bin/python scripts/setup.py
```

## 5. Connect it to Claude (Claude desktop app)

1. Claude desktop → **Settings → Developer → Edit Config**.
2. Paste the contents of `igmcp/claude_desktop_config.example.json` and replace `YOUR-MAC-USERNAME` with your username. Run `whoami` in Terminal if you're not sure.
3. Restart the Claude desktop app. The `instagram` tools appear in chats on this Mac.

Then tell Claude whether the morning task should **post automatically**, or **prepare the post and wait for your OK**. Automatic posting needs your Mac awake with the Claude app open at 06:51.

## Renewing the token

The token lasts 60 days. Repeat step 3.4 before it expires and replace the token in `.env`.

## Licence and sources

Funding information comes from festival catalogues, film funds and trade press, linked under each film in `films.json`. ig-mcp © its authors, MIT licence.
