#!/usr/bin/env python3
"""Film metadata + Funding articles for two-step. Writes films.json.
Each film: id, title, match (title variants used by venues), year, country, director,
kind, backing (money-type tags), studios, public, broadcasters, distributors, sales,
budget, funding (short article), sources."""
import json

W = "https://en.wikipedia.org/wiki/"
F = []
def film(id, title, match, year, country, director, kind, backing, funding, sources,
         studios=(), public=(), broadcasters=(), distributors=(), sales=(), budget=None):
    F.append(dict(id=id, title=title, match=list(match), year=year, country=country, director=director,
                  kind=kind, backing=list(backing), studios=list(studios), public=list(public),
                  broadcasters=list(broadcasters), distributors=list(distributors), sales=list(sales),
                  budget=budget, funding=funding, sources=list(sources)))

# ---------------- new releases ----------------
film("coward", "Coward", ["Coward"], 2026, "BE/FR/NL", "Lukas Dhont", "new release",
     ["Belgian production", "European public funds", "Arthouse producers"],
     "Lukas Dhont's third feature is led by his Belgian company The Reunion, with Lumen (France), Topkapi Films (Netherlands) and Versus (Belgium) as co-producers. Brussels' regional fund put in €125,000, which it lists as about 1.2% of the budget, so the film cost roughly €10 million. The Match Factory sells it abroad and Diaphana releases it in France.",
     ["https://www.festival-cannes.com/en/f/coward/", "https://screen.brussels/en/project/coward"],
     studios=["The Reunion", "Lumen", "Topkapi Films", "Versus"], public=["screen.brussels"],
     distributors=["Diaphana (FR)"], sales=["The Match Factory"], budget="≈ €10.5M (derived from screen.brussels share)")
film("digger", "Digger", ["Digger"], 2026, "US", "Alejandro G. Iñárritu", "new release",
     ["Hollywood studio"],
     "A Hollywood studio picture: Legendary Pictures produced it in partnership with Warner Bros., which also distributes it. Tom Cruise is a producer alongside Iñárritu and Mary Parent. Warner Bros. says the budget stayed at $125 million; reports of $160–180 million were denied by the studio.",
     [W + "Digger_(2026_film)"],
     studios=["Legendary Pictures", "Warner Bros. Pictures"], distributors=["Warner Bros. Pictures"], budget="$125M (studio figure)")
film("social-reckoning", "The Social Reckoning", ["The Social Reckoning"], 2026, "US", "Aaron Sorkin", "new release",
     ["Hollywood studio"],
     "Made by Sony's Columbia Pictures with Alcon Entertainment and released worldwide by Sony Pictures. The reported budget is $30–42 million, modest for a studio film with this cast.",
     [W + "The_Social_Reckoning"],
     studios=["Columbia Pictures (Sony)", "Alcon Entertainment"], distributors=["Sony Pictures"], budget="$30–42M")
film("primetime", "Primetime", ["Primetime"], 2026, "US", "Lance Oppenheim", "new release",
     ["US indie studio"],
     "A24 both finances and distributes this one. Robert Pattinson produces through his company Icki Eneo Arlo, with Range Media Partners and Square Peg also credited. No budget has been published.",
     [W + "Primetime_(2026_film)"],
     studios=["A24", "Icki Eneo Arlo", "Range Media Partners", "Square Peg"], distributors=["A24"])
film("the-invite", "The Invite", ["The Invite"], 2026, "US", "Olivia Wilde", "new release",
     ["US indie studio"],
     "Produced by Megan Ellison's Annapurna, then sold at Sundance 2026. A24 won a days-long bidding war against Focus Features and paid more than $12 million for the rights.",
     ["https://au.variety.com/2026/film/news/olivia-wilde-the-invite-sells-to-a24-sundance-32427"],
     studios=["Annapurna"], distributors=["A24"], budget="Rights sold for $12M+")
film("sense-sensibility", "Sense and Sensibility", ["Sense and Sensibility"], 2026, "UK", "Georgia Oakley", "new release",
     ["Hollywood studio"],
     "Working Title Films produced it with November Pictures and Kiddo Films. Working Title belongs to Universal, which releases the film internationally while its arthouse label Focus Features handles the US.",
     [W + "Sense_and_Sensibility_(2026_film)"],
     studios=["Working Title Films", "November Pictures", "Kiddo Films"], distributors=["Focus Features (US)", "Universal Pictures (intl)"])
film("garance", "Garance", ["Garance"], 2026, "FR/BE", "Jeanne Herry", "new release",
     ["French independent producers", "European studio"],
     "Produced in France by Chi-Fou-Mi Productions and Trésor Films, with Belgium's Artémis Productions as the foreign partner. StudioCanal distributes it in France and sells it internationally.",
     ["https://www.unifrance.org/film/63383"],
     studios=["Chi-Fou-Mi Productions", "Trésor Films", "Artémis Productions"], distributors=["StudioCanal"], sales=["StudioCanal"])
film("espece-explosive", "L'Espèce explosive", ["L'Espèce explosive"], 2026, "FR", "Sarah Arnold", "new release",
     ["European public funds", "French independent producers"],
     "A debut feature produced by 5à7 Films and built on public money. The Grand Est region backed it first, and France's CNC gave writing aid, an advance on receipts, music aid and distribution aid. The director says the CNC advance, won on the third try, unlocked the rest of the financing.",
     ["https://www.cnc.fr/cinema/actualites/des-mots-aux-decors-tout-est-sujet-a-creativite---rencontre-avec-sarah-arnold-realisatrice-de--lespece-explosive_2672638"],
     studios=["5à7 Films"], public=["CNC", "Région Grand Est"], distributors=["Pan Distribution"], sales=["Playtime"])
film("last-one-road", "The Last One for the Road", ["The Last One for the Road"], 2025, "IT/DE", "Francesco Sossai", "new release",
     ["European public funds", "TV broadcaster"],
     "Original title Le città di pianura. Vivo Film produced it with Germany's Maze Pictures and Rai Cinema, the film arm of Italy's public broadcaster. Italy's culture ministry and the Council of Europe fund Eurimages also contributed.",
     ["https://cineuropa.org/it/film/477285/"],
     studios=["Vivo Film", "Maze Pictures"], public=["Italian Ministry of Culture (DGCA)", "Eurimages"], broadcasters=["Rai Cinema"],
     distributors=["Lucky Red (IT)"], sales=["Lucky Number"])
film("naza", "Naza", ["Naza"], 2026, "UK/US", "Yuval Abraham, Rachel Szor", "new release",
     ["Media company", "Independent producers"],
     "A documentary from the No Other Land team, produced by James Wilson's JW Films with The Guardian, in association with Placeholder Films and Unseen Hand. Jonathan Glazer is an executive producer and mk2 Films handles world sales.",
     ["https://www.screendaily.com/news/venice-competition-title-naza-about-gaza-war-boarded-for-sales/5219667.article"],
     studios=["JW Films", "The Guardian", "Placeholder Films", "Unseen Hand"], sales=["mk2 Films"])
film("notre-salut", "Notre salut", ["Notre salut"], 2026, "FR/BE", "Emmanuel Marre", "new release",
     ["Belgian production", "European public funds", "TV broadcaster"],
     "A Franco-Belgian co-production by Kidam and Brussels-based Michigan Films, made for under €5 million. Co-producers include France 2 Cinéma, Belgium's public broadcaster RTBF and Be tv/Proximus, and the CNC gave an advance on receipts plus development and distribution aid.",
     ["https://www.cnc.fr/cinema/actualites/dans-lequipe-personne-navait-fait-de-film-depoque----notre-salut--raconte-par-son-producteur_2668989"],
     studios=["Kidam", "Michigan Films"], public=["CNC"], broadcasters=["France 2 Cinéma", "RTBF", "Be tv / Proximus"], budget="< €5M")
film("rose", "Rose", ["Rose"], 2026, "AT/DE", "Markus Schleinzer", "new release",
     ["Arthouse producers", "Streamer"],
     "An Austrian-German co-production by Schubert, ROW Pictures and Walker & Worm Film. The Match Factory sells it, and the streamer Mubi bought it for North and Latin America, the UK, Italy and other territories.",
     [W + "Rose_(2026_film)"],
     studios=["Schubert", "ROW Pictures", "Walker & Worm Film"], distributors=["Filmladen (AT)", "Piffl Medien (DE)", "Mubi"], sales=["The Match Factory"])
film("sorry", "Tegenwoordig heet iedereen sorry", ["Tegenwoordig heet iedereen sorry"], 2026, "BE/DE", "Frederike Migom", "new release",
     ["Belgian production", "Arthouse producers"],
     "A Flemish youth film produced by Ivy Vanhaecke at deMENSEN, with Germany's CALA Filmproduktion and Juliet at Pupkin. LevelK sells it abroad. The listing we found names no public funds.",
     ["https://cineuropa.org/film/487611"],
     studios=["deMENSEN", "CALA Filmproduktion", "Juliet at Pupkin"], distributors=["Paradiso (NL)"], sales=["LevelK"])
film("franz", "Franz", ["Franz"], 2025, "CZ/DE/PL", "Agnieszka Holland", "new release",
     ["European public funds", "TV broadcaster"],
     "A Kafka biopic stitched together from many public sources. Marlene Film (Prague), X Filme (Berlin) and Metro Films (Warsaw) produced it, joined by Czech, Polish and German broadcasters and Canal+. Funding came from Eurimages, the Czech Audiovisual Fund, the Polish Film Institute, Medienboard Berlin-Brandenburg and Germany's DFFF.",
     ["https://www.filmcenter.gov.cz/en/news/a-literary-icon-comes-alive-in-agnieszka-holland-s-kafkaesque-bio-pic-franz"],
     studios=["Marlene Film Production", "X Filme Creative Pool", "Metro Films", "Barrandov Studio"],
     public=["Eurimages", "Czech Audiovisual Fund", "Polish Film Institute", "Medienboard Berlin-Brandenburg", "DFFF"],
     broadcasters=["Czech Television", "Telewizja Polska", "Canal+", "ZDF/ARTE"], sales=["Films Boutique"])
film("memoire-fille", "Mémoire de fille", ["Mémoire de fille"], 2026, "FR", "Judith Godrèche", "new release",
     ["French independent producers"],
     "Judith Godrèche's adaptation of Annie Ernaux is produced by Windy Production. Paradise City Sales handles international sales and Jour2Fête releases it in France.",
     ["https://www.festival-cannes.com/en/f/memoire-de-fille/"],
     studios=["Windy Production"], distributors=["Jour2Fête (FR)"], sales=["Paradise City Sales"])
film("minotaur", "Minotaur", ["Minotaur"], 2026, "FR/DE/LV", "Andrey Zvyagintsev", "new release",
     ["Arthouse producers", "TV broadcaster"],
     "A French-German-Latvian co-production led by MK Productions and CG Cinema, with Forma Pro Films, Razor Film and ARTE France Cinéma. mk2 Films sells it and Les Films du Losange distributes it; France picked it as its Oscar entry.",
     ["https://cineuropa.org/film/490431/"],
     studios=["MK Productions", "CG Cinema", "Forma Pro Films", "Razor Film"], broadcasters=["ARTE France Cinéma"],
     distributors=["Les Films du Losange"], sales=["mk2 Films"])
film("odyssey", "The Odyssey", ["The Odyssey"], 2026, "US/UK", "Christopher Nolan", "new release",
     ["Hollywood studio"],
     "Universal Pictures financed and distributes it, produced with Nolan and Emma Thomas's company Syncopy. At about $250 million it is one of Nolan's most expensive films. Studio Skoop shows it on 35mm.",
     [W + "The_Odyssey_(2026_film)"],
     studios=["Universal Pictures", "Syncopy"], distributors=["Universal Pictures"], budget="≈ $250M")
film("dune3", "Dune: Part Three", ["Dune: Part Three"], 2026, "US", "Denis Villeneuve", "new release",
     ["Hollywood studio"],
     "Legendary Entertainment and Warner Bros. produce it, as with the first two parts, and it was shot at Origo Studios in Hungary. No budget has been published.",
     ["https://www.screenglobalproduction.com/news/2025/07/09/dune-part-three-begins-production-hungary"],
     studios=["Legendary Entertainment", "Warner Bros."], distributors=["Warner Bros."])
film("wicker", "Wicker", ["Wicker"], 2026, "US", "Eleanor Wilson, Alex Huston Fischer", "new release",
     ["Independent financiers"],
     "Financed by Tango and Topic Studios, with development money from Votiv; South of The River and Yoki also produce. Black Bear bought it at Sundance 2026 for North America and the UK and handles international sales.",
     ["https://www.thewrap.com/creative-content/movies/wicker-movie-release-olivia-colman-alexander-skarsgard-black-bear/"],
     studios=["South of The River", "Yoki, Inc.", "Votiv"], public=[], distributors=["Black Bear"], sales=["Black Bear"])
film("golden-spurtle", "The Golden Spurtle", ["The Golden Spurtle (2025)"], 2025, "AU", "Constantine Costi", "new release",
     ["Public funds (non-EU)"],
     "A small documentary produced by Hytra Films in Australia, with development and production support from the public agency Screen Australia.",
     ["https://www.screenaustralia.gov.au/the-screen-guide/t/the-golden-spurtle/41938"],
     studios=["Hytra Films"], public=["Screen Australia"])
# ---------------- family ----------------
film("yugly", "Yugly", ["Yugly", "Mochy"], 2026, "BE/FR", "Yanis Belaid, Jérémie Degruson", "family",
     ["Belgian production", "Tax shelter"],
     "Brussels animation studio nWave made it with Octopolis. The Belgian tax shelter, raised through Umedia, and screen.brussels helped pay for it. Shown as Mochy in French.",
     ["https://umedia.eu/news/four-umedia-animated-projects-were-selected-for-the-2026-annecy-festival/"],
     studios=["nWave Studios", "Octopolis", "Umedia"], public=["Belgian tax shelter", "screen.brussels"])
film("jungle", "Born in the Jungle", ["Born in the Jungle", "Magische Jungle"], 2026, "LV/PL/CZ", "Edmunds Jansons", "family",
     ["Independent animation studios"],
     "A Latvian-Polish-Czech animation by Atom Art, Letko and Hausboot. Shown as Magische Jungle at Studio Skoop. Sources we found name no funders.",
     ["https://fantoche.ch/en/gramme/Born-in-the-Jungle~prg3562"],
     studios=["Atom Art", "Letko", "Hausboot"])
film("reverie", "La Grande rêvasion", ["La Grande rêvasion"], 2025, "FR/BE", "Rémi Durin", "family",
     ["TV broadcaster", "Independent animation studios"],
     "A 45-minute animation made for television by Autour de Minuit and Kwassa Films, co-produced by Canal+. It won the Annecy Cristal for TV production.",
     ["https://en.unifrance.org/news/17480/la-grande-revasion-une-ode-a-l-imagination-et-a-l-aventure-recompensee-a-annecy-par-le-cristal-de-la-meilleure-production-tv"],
     studios=["Autour de Minuit", "Kwassa Films"], broadcasters=["Canal+", "RTS"], distributors=["Le Parc Distribution (BE)"])
film("pout-pout", "The Pout-Pout Fish", ["The Pout-Pout Fish"], 2026, "AU/US", "Ricard Cussó", "family",
     ["Independent animation studios"],
     "An independently financed animation made for under $10 million by MIMO Studios, Like a Photon Creative, Cosmic Dino Studio, Alceon Entertainment and Eclectik Vision.",
     [W + "The_Pout-Pout_Fish_(film)"],
     studios=["MIMO Studios", "Like a Photon Creative", "Cosmic Dino Studio", "Alceon Entertainment", "Eclectik Vision"], budget="< $10M")
film("shaun", "Shaun het Schaap: Het Beest op de Boerderij", ["Shaun het Schaap: Het Beest op de Boerderij"], 2026, "UK", "Aardman", "family",
     ["European studio", "TV broadcaster"],
     "Aardman made it as a Sky Original: Sky releases it in the UK and StudioCanal everywhere else. Original title The Beast of Mossy Bottom.",
     ["https://aardman.com/latest-news/2025/may/new-shaun-the-sheep-movie-announced-for-2026"],
     studios=["Aardman"], broadcasters=["Sky"], distributors=["Sky (UK)", "StudioCanal"])
# ---------------- repertory ----------------
film("devils", "The Devils (1971)", ["The Devils (1971)"], 1971, "UK", "Ken Russell", "repertory",
     ["Hollywood studio"],
     "Warner Bros. financed Ken Russell's film through Russo Productions and then cut it heavily for release. The new 4K restoration brings back material the studio removed.",
     [W + "The_Devils_(film)"], studios=["Russo Productions", "Warner Bros."], distributors=["Warner Bros."])
film("trainspotting", "Trainspotting (1996)", ["Trainspotting (1996)"], 1996, "UK", "Danny Boyle", "repertory",
     ["TV broadcaster"],
     "Paid for by Channel Four Films, the film arm of the UK public-service broadcaster, and produced by Figment Films. PolyGram released it.",
     [W + "Trainspotting_(film)"], studios=["Figment Films"], broadcasters=["Channel Four Films"], distributors=["PolyGram"])
film("akira", "Akira (1988)", ["Akira (1988)"], 1988, "JP", "Katsuhiro Otomo", "repertory",
     ["Japanese production committee"],
     "Funded by the Akira Committee, a Japanese production committee of companies including publisher Kodansha, Mainichi Broadcasting, toy maker Bandai, ad agency Hakuhodo and Toho. Tokyo Movie Shinsha animated it.",
     [W + "Akira_(1988_film)"], studios=["Akira Committee", "Tokyo Movie Shinsha"], distributors=["Toho"])
film("werewolf", "An American Werewolf in London", ["An American Werewolf in London"], 1981, "UK/US", "John Landis", "repertory",
     ["Hollywood studio"],
     "PolyGram Pictures financed it with The Guber-Peters Company, and Universal released it.",
     [W + "An_American_Werewolf_in_London"], studios=["PolyGram Pictures", "Guber-Peters Company"], distributors=["Universal Pictures"])
film("donnie", "Donnie Darko (2001)", ["Donnie Darko (2001)"], 2001, "US", "Richard Kelly", "repertory",
     ["Independent financiers"],
     "An independent film financed by Pandora Cinema with Drew Barrymore's Flower Films, released in the US by Newmarket Films.",
     [W + "Donnie_Darko"], studios=["Pandora Cinema", "Flower Films", "Adam Fields Productions"], distributors=["Newmarket Films"])
film("shall-we-dance", "Shall We Dance? (1996)", ["Shall We Dance? (1996)"], 1996, "JP", "Masayuki Suo", "repertory",
     ["Japanese production committee", "TV broadcaster"],
     "Backed by Nippon TV, ad agency Hakuhodo, distributor Nippon Shuppan Hanbai and the studio Daiei. Toho released it in Japan and Miramax bought it for the US.",
     [W + "Shall_We_Dance%3F_(1996_film)"], studios=["Daiei", "Hakuhodo", "Nippon Shuppan Hanbai"], broadcasters=["Nippon TV"], distributors=["Toho (JP)", "Miramax (US)"])
film("return", "The Return (2003)", ["The Return (2003)"], 2003, "RU", "Andrey Zvyagintsev", "repertory",
     ["Independent producers"],
     "Zvyagintsev's debut was produced by REN Film, the Moscow company of Dmitry Lesnevsky. Shown alongside his new film Minotaur.",
     [W + "The_Return_(2003_film)"], studios=["REN Film"])
film("hard-ticket", "Hard Ticket to Hawaii", ["Hard Ticket to Hawaii"], 1987, "US", "Andy Sidaris", "repertory",
     ["Self-financed"],
     "A Sidaris family production: Andy and Arlene Sidaris made it through their own Malibu Bay Films for the video market.",
     [W + "Hard_Ticket_to_Hawaii"], studios=["Malibu Bay Films"])
film("offside", "Offside (2006)", ["Offside (2006)"], 2006, "IR", "Jafar Panahi", "repertory",
     ["Self-financed"],
     "Produced by Jafar Panahi's own company and shot partly during a real qualifying match, without official backing in Iran. Sony Pictures Classics released it in the US.",
     [W + "Offside_(2006_film)"], studios=["Jafar Panahi Film Productions"], distributors=["Sony Pictures Classics (US)"])
film("mortu-nega", "Mortu Nega (1988)", ["Mortu Nega (1988)"], 1988, "GW", "Flora Gomes", "repertory",
     ["Public funds (non-EU)"],
     "Made by Guinea-Bissau's National Film Institute, the state body that produced the country's first fiction feature after independence.",
     [W + "Mortu_Nega"], studios=["Instituto Nacional de Cinema da Guiné-Bissau"])
film("gypsies", "Time of the Gypsies (1988)", ["Time of the Gypsies (1988)"], 1988, "YU", "Emir Kusturica", "repertory",
     ["Hollywood studio"],
     "Produced by Forum Sarajevo with Mirza Pašić and Bond producer Harry Saltzman, and distributed by Columbia Pictures.",
     [W + "Time_of_the_Gypsies"], studios=["Forum Sarajevo"], distributors=["Columbia Pictures"])
film("near-dark", "Near Dark (1987)", ["Near Dark (1987)"], 1987, "US", "Kathryn Bigelow", "repertory",
     ["Independent financiers"],
     "A $5 million independent production by F/M Entertainment, distributed by the De Laurentiis Entertainment Group.",
     [W + "Near_Dark"], studios=["F/M Entertainment"], distributors=["De Laurentiis Entertainment Group"], budget="$5M")
film("fat-city", "Fat City (1972) + For Mouna", ["Fat City (1972) + For Mouna"], 1972, "US", "John Huston", "repertory",
     ["Hollywood studio"],
     "Ray Stark's Rastar produced Fat City for Columbia Pictures. The opening short For Mouna is a 2023 Belgian short by Spencer Bogaert.",
     [W + "Fat_City_(film)"], studios=["Rastar"], distributors=["Columbia Pictures"])
film("iron-giant", "De Ijzeren Reus (1999)", ["De Ijzeren Reus (1999)"], 1999, "US", "Brad Bird", "repertory",
     ["Hollywood studio"],
     "The Iron Giant was made by Warner Bros. Feature Animation, the studio's in-house animation unit.",
     [W + "The_Iron_Giant"], studios=["Warner Bros. Feature Animation"], distributors=["Warner Bros."])
film("coyote", "Coyote Ugly + Cocktail", ["Coyote Ugly + Cocktail"], 2000, "US", "David McNally / Roger Donaldson", "repertory",
     ["Hollywood studio"],
     "Both are Disney films released under its Touchstone label: Coyote Ugly with Jerry Bruckheimer Films, Cocktail with the investment fund Silver Screen Partners.",
     [W + "Coyote_Ugly_(film)", W + "Cocktail_(1988_film)"], studios=["Touchstone (Disney)", "Jerry Bruckheimer Films", "Silver Screen Partners"])
film("damned", "Damned if You Don't + Dildotectónica", ["Damned if You Don't + Dildotectónica"], 1987, "US/PT", "Su Friedrich, Paula Tomás Marques", "repertory",
     ["Self-financed"],
     "Su Friedrich makes her experimental films largely on her own. We found no funding details for the 2023 Portuguese short Dildotectónica.",
     [W + "Su_Friedrich"], studios=["Su Friedrich (independent)"])
film("bruges", "Apolline + Bruges-La-Morte", ["Apolline + Bruges-La-Morte"], 1978, "BE/US", "Lucien Deroisy, Ronald Chase", "repertory",
     ["Unknown"],
     "Two rarely shown adaptations, one shot in Ghent in 1959. We could not find reliable information on who financed either film.",
     ["https://kaskcinema.be/film/apolline-bruges-la-morte/"])
# ---------------- programmes / events ----------------
for id, t, desc, url in [
    ("love-slug", "Love That Moves the Slug", "Short-film programme curated by artist Anouk De Clercq; many different makers.", "https://kaskcinema.be/film/love-that-moves-the-slug/"),
    ("kidscinema", "KIDScinema: The Best of Filem'On", "Short films for children from the Filem'On festival.", "https://kaskcinema.be/film/kidscinema-the-best-of-filemon/"),
    ("horror", "Night of the Horror: Bad Trip", "Triple bill with Kuru: A Lizard in a Woman's Skin (1971), MadS and Brain Damage (1988).", "https://kaskcinema.be/film/night-of-the-horror-bad-trip/"),
    ("freeride", "Freeride Filmfestival", "Touring programme of ski and snowboard films.", "https://www.studioskoop.be/agenda-studio-skoop/"),
    ("cineconcert", "Cinéconcert voor kinderen", "Live music to short films for children, with FilemKING.", "https://dekoer.be/programma/cineconcert-voor-kinderen-kinderfilm/"),
    ("inmate", "Inmate Sessions Live!", "Cine-concert and talk about cinema in Ghent prison.", "https://dekoer.be/programma/inmate-sessions-live/")]:
    film(id, t, [t], None, "", "various", "programme", ["Programme of several films"],
         desc + " Funding is not tracked for mixed programmes.", [url])

json.dump({"films": F}, open("films.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(F), "films")
