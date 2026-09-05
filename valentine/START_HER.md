# Valentine – fanlaget Blender-scene

Åpne **Valentine_Fan_Recreation.blend**. Det er hovedfilen. Modeller, materialer, lys, Arthur og kameraer er redigerbare. Teksturer er pakket inn i filen, og skiltene er gjort om til geometri slik at de ikke krever en installert skrifttype.

Dette er en detaljert første versjon av hovedgaten og miljøet rundt, med Smithfield's Saloon som hovedmotiv. Scenen har 18 bygninger, 49 innpakkede teksturbilder og fem kameravinkler. Den er laget og kontrollert i Blender 5.1.2 på denne Macen.

## Se deg rundt

Filen åpnes med hovedkameraet. Bytt det aktive bildet på tidslinjen nederst mellom **1 og 5** for å velge kameravinkel:

| Bilde | Kameravinkel | Ferdig stillbilde |
| --- | --- | --- |
| 1 | Smithfield's og hovedgaten | [Åpne bilde](renders/01_Smithfields_Main_Street.png) |
| 2 | Langs hovedgaten | [Åpne bilde](renders/02_Along_Main_Street.png) |
| 3 | Saints Hotel og banken | [Åpne bilde](renders/03_Saints_Hotel_and_Bank.png) |
| 4 | Oversikt over hovedgaten | [Åpne bilde](renders/04_Town_Overview.png) |
| 5 | Arthur ved saloonen | [Åpne bilde](renders/05_Arthur_at_Smithfields.png) |

Dette er fem kameravalg, ikke en animasjon. De ferdige bildene ligger i `renders/` og er 2560 × 1600 piksler, rendret med Cycles, 112 prøver og støyfjerning.

For å navigere fritt: bruk View → Cameras → Active Camera for å gå ut av kameravisningen, eller roter visningen med navigasjonskontrollen oppe til høyre. Samlingene i Outliner til høyre er navngitt etter terreng, bygninger, rekvisitter, Arthur, lys og kameraer. Originalene til gjenbrukbare rekvisitter og trær er skjult i samlinger som begynner med `00`; instansene deres er synlige i scenen.

Material Preview er raskere når du redigerer. De lagrede Cycles-bildene viser den ferdige belysningen og refleksjonene. Bruk File → Save As og et nytt filnavn dersom du vil eksperimentere med en egen kopi.

## Hva som er bygget

Smithfield's, Worth's General Store, Keane's byggearbeid, doktor, sheriff, smie, Saints Hotel, bank, advokatkontor og våpenbutikk danner hovedgaten. Utenfor gaten finnes blant annet jernbanestasjon, vanntårn, stall, hus, kirke og innhegninger.

Miljøet har individuelt modellerte kledningsbord og takspon, vindusrammer, verandaer, trapper, skorsteiner, tønner med staver og jernbånd, trekasser, benker, vogner med eikehjul, lykter, barberstang, skilt, telegrafledninger, hjulspor, vannpytter, grus, trær og gress. Arthur kommer fra GLB-filen du la ved; riggen er beholdt og armene er posert ned i en stående positur.

## Referanser og avgrensning

Fasadetrekkene er basert på bilder fra spillet og en original artists portefølje. Bygningsmål, baksider, perifere tomter, rekvisittplassering og deler av terrenget er egne tolkninger. Dette er derfor ikke en målfast kopi av hele spillkartet. Interiørene er enkle rombakgrunner; saloonen har noe innvendig geometri bak døren, men byen har ikke fullt innredede interiører, befolkningssimulering eller animasjon.

- [Smithfield's – spillreferanse](https://guides4gamers.com/red-dead-redemption-2/quests/americans-at-rest/)
- [Hovedgaten og nabobygg – spillreferanse](https://guides4gamers.com/red-dead-redemption-2/quests/a-quiet-time/)
- [Saints Hotel – original artists portefølje](https://dhanasekaran.artstation.com/projects/w0WP56)
- [Poly Haven – materialkilde](https://polyhaven.com/)

Tre- og jordskanningene er fra Poly Haven, med CC0-lisens. Detaljert kildeinformasjon og nedlastingskontroller står i `reference/SOURCES.json` og `textures/SOURCES.json`. Arthurs opphav/lisens fulgte ikke med filen; scenen er levert lokalt og er ikke publisert. Red Dead Redemption 2 og figurene tilhører sine respektive rettighetshavere.

Den generiske saloon-filen du la ved ligger urørt i mappen over. Den ble ikke brukt som Smithfield's, fordi fasaden ikke samsvarer med referansen. Arthur-originalen er også bevart.

## Bevaring og teknisk kontroll

`checkpoints/` inneholder sikkerhetskopier. Kubedokumentet som var åpent før byen ble vist, er bevart som `Blender_Untitled_before_Valentine_2026-09-05_1711.blend`.

`verification.json` dokumenterer gjenåpning, påkrevde samlinger, teksturer, endelige koordinater, kameraplassering og kontrollsum for Arthur-originalen. `render_final_report.json` dokumenterer de fem rendringene. `delivery_manifest.json` inneholder kontrollsummer og bildefilkontroll for den leverte versjonen.

Byggekoden ligger i `scripts/`, og teksturene i `textures/`. De er beholdt for videreutvikling; de trengs ikke for å åpne den pakkede Blender-filen. **build_scene.py skriver hovedfilen på nytt**. Lag en egen kopi av manuelle endringer før du kjører byggeren igjen.
