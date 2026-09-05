# Valentine — plan for en detaljert fan-rekonstruksjon i Blender

Undersøkt 5. september 2026. Valgt retning: Valentine, med saloonen og den gjørmete hovedgaten som første område.

**Status: Research og modellkontroll er gjennomført. Selve Valentine-rekonstruksjonen er ikke modellert ennå.** `Asset_Review.blend` inneholder inspeksjonsscener av de to vedlagte modellene, med lys og kameraer. Den er ikke en ferdig byscene.

## Anbefalt første leveranse

Et sammenhengende gateutsnitt rundt Smithfield’s Saloon, med den gjenkjennelige fasaden som hovedmotiv, nærmeste nabofasader, treplattinger og et detaljert parti av veien. Resten av byen bygges først som en enkel oversikt over bygninger og terreng, slik at vi kan utvide uten å miste riktig plassering og målestokk.

Første vurderingsbilder: ett gatebilde i menneskehøyde, ett nærmere bilde av inngangen, og ett oversiktsbilde som viser plasseringene. Et mulig uttrykk er overskyet ettermiddag etter regn, med vått treverk og pytter. Dette er et kreativt forslag, ikke et allerede godkjent lysoppsett.

## Hva de vedlagte filene gir oss

| Fil | Verifisert innhold | Anbefalt bruk |
| --- | --- | --- |
| `../saloon_with_textures.glb` | 6 010 trekanter, 15 materialer, 40 innebygde teksturbilder på 2 048 × 2 048. Normal- og metallic/roughness-teksturer er tilordnet alle 15 materialene. | Material- og lysprøver, eventuelt et separat western-motiv. Geometrien passer ikke som ferdig Smithfield’s-fasade. |
| `../artur/source/ArthurMorgan.glb` | Kildens 21 mesh-deler har samlet 57 795 trekanter, 19 materialer, 38 innebygde bilder og ett skjelett med 962 ledd. Ingen animasjoner er inkludert. Normalteksturer er tilordnet; egne metallic/roughness-bilder mangler. | Karakter og størrelsesreferanse etter skalakontroll. Posering, bevegelse og materialjustering må kontrolleres særskilt. |

Begge modellene er importert og rendret i Blender 5.1.2. De innebygde bildene kan leses. Arthur vises i en utgangspose med armene ut; dette bekrefter ikke at skjelettet er animasjonsklart. Teksturene har varierende oppløsning, og flere av Arthurs bilder er små. Derfor bør han først vurderes i et helfigurbilde fremfor et ekstremt nærbilde av ansiktet.

Den vedlagte saloonen har hjørneinngang, balkong langs to sider og et enkelt, lyst uttrykk. Det undersøkte spillbildet av Smithfield’s viser en bred front med falmet rødlig panel, et stort malt navneskilt og en overbygd inngang. Å bygge den riktige fasaden fra referanser vil gi en mer trofast rekonstruksjon enn å detaljere feil bygning. Se [originalt spillbilde hos Guides for Gamers](https://guides4gamers.com/red-dead-redemption-2/quests/americans-at-rest/) og den lokale forhåndsvisningen `saloon_b.png`.

Saloonens innebygde metadata oppgir gallacs som skaper og CC-BY-4.0 som lisens, med [denne Sketchfab-siden](https://sketchfab.com/3d-models/saloon-with-textures-dcca8bb7ca8740299d81f9b384d2e709) som kilde. Nettsiden kunne ikke hentes i søkeverktøyet; lisensopplysningen er derfor kun kontrollert i filmetadata. Arthur-filen inneholder ingen tilsvarende opplysning. Opprinnelse og eventuelle delingsvilkår må avklares dersom modellfiler senere skal distribueres.

## Byggerekkefølge

1. **Samle referanser som hører sammen.** Bruk bilder fra samme del av spillet og samme bytilstand. Lag en oversikt over saloonens front, sider, tak og nabobygninger. Merk usette flater som ukjente; de skal ikke fremstilles som bekreftet nøyaktige. Kart og andre fans’ rekonstruksjoner kan støtte orienteringen, men spillbilder bestemmer arkitekturen. Rockstar dokumenterer at [Photo Mode har fri kamerabevegelse](https://www.rockstargames.com/newswire/article/75o941131a8257/Red-Dead-Redemption-2-Photo-Mode-and-Story-Mode-Additions-Now-Availabl), som er nyttig for målrettet referansefangst.

2. **Kontroller målestokk og gateplan.** Lag en enkel modell av bygningene, plattinghøydene, veien og terrenget. Bruk dører og menneskehøyde som foreløpige holdepunkter, og sjekk disse mot flere bilder. Importerte dimensjoner er ikke i seg selv bevis på riktig målestokk. Velg kameraer tidlig og sammenlign silhuetter og avstander før detaljering.

3. **Bygg Smithfield’s og et lite bibliotek med bygningsdeler.** Lag gjenbrukbare panelbord, stolper, vinduer, dører, trappetrinn, taklister og plattinger. Gjør hovedfasaden unik der referansene krever det. Gjenbruk delene i nabobygningene, med kontrollerte forskjeller i høyde, farge og slitasje. Dette følger samme grunnprinsipp som [Praveen Rajs Valentine-prosjekt](https://praveenraj2.artstation.com/projects/6LPZ4x): modellene ble laget i Blender som moduler, mens sluttmiljøet ble satt sammen i Unreal Engine 5. Vi kan beholde både bygging og rendering i Blender.

4. **Bygg gjørmen i flere nivåer.** Form veiens store ujevnheter og hjulspor i geometri. Legg på mindre jordklumper, støvel- og hovspor der kameraet faktisk ser dem. Bland tørre kanter og våte partier med ulike farger, overflateruhet og dybde. Plasser vann i lavpunktene. Unngå at hele veien blir en jevnt blank flate. [Brown Mud](https://polyhaven.com/a/brown_mud) og [Mud Forest](https://polyhaven.com/a/mud_forest) er mulige grunnmaterialer; de gjenskaper ikke Valentines spor og veiprofil av seg selv.

5. **Legg på materialer og synlig håndverk.** Bruk faktisk geometri til detaljer som endrer omriss eller gir tydelige skygger: bordkanter, sprekker mellom paneler, beslag og utspring. Bruk normal- og høydekart til mindre overflatevariasjon. Tilpass slitasjen til vann, vær og bruk, særlig ved bakken, trappene og døråpningene. Dhanasekaran Muthusamy beskriver skannet, repeterbart treverk i sitt arbeid på [Saints Hotel i Valentine](https://dhanasekaran.artstation.com/projects/w0WP56), og viser bilder fra selve spillet. [Rough Wood fra Poly Haven](https://polyhaven.com/a/rough_wood) er en mulig materialbase, med CC0 oppgitt på siden.

6. **Plasser rekvisitter med hensikt.** Hestebommer, tønner, kasser, plakater og avfall følger referansene og aktiviteten på stedet. Bruk Geometry Nodes eller delte mesh-kopier til gjentatte detaljer. Blender beskriver at [instanser gjenbruker geometri uten å kopiere alle dataene](https://docs.blender.org/manual/en/4.5/modeling/geometry_nodes/instances.html). Behold instansene så lenge vi ikke trenger å gjøre dem til egne mesh-objekter.

7. **Lyssett og kontroller resultatet.** Bruk enkle forhåndsvisninger mens vi bygger, og små Cycles-prøver for å bedømme lys, våte flater og materialer. Kontroller først nøytralt lys, så det ønskede uttrykket. Legg Arthur inn når målestokk og omgivelser fungerer. En stillestående figur er første trinn; en gående figur krever et eget, kontrollert animasjonsoppsett.

8. **Utvid byen fra det kontrollerte gateutsnittet.** Gjenbruk delene og materialene, bygg neste gate eller kvartal, og behold enklere geometri på større avstand. Full byoversikt og svært detaljerte nærbilder har ulike behov; detaljnivå må følge kamerabruken. Start med utvendige miljøer. Rom som skal ses gjennom vinduer eller innganger prioriteres før fullstendige interiører.

## Hva som må være riktig før første utsnitt kalles ferdig

- Smithfield’s har gjenkjennelige proporsjoner, skilt, inngang og naboforhold i bilder som kan sammenlignes med spillet.
- Bygninger, karakter, trappetrinn og gatemøbler deler en troverdig målestokk.
- Veien har synlige høydeforskjeller, spor og variasjon mellom våte og tørre områder.
- Detaljer tåler avstanden i de valgte kameraene; ingen synlige manglende teksturer eller tydelig repetisjon i hovedmotivet.
- Blender-filen kan åpnes igjen med nødvendige teksturer tilgjengelige.
- Forhåndsvisninger og en senere endelig render rapporteres som separate resultater.

## Leveranser fra denne undersøkelsen

- `Asset_Review.blend`: separate inspeksjonsscener for saloonen og Arthur, med pakkede teksturer.
- `saloon_a.png`, `saloon_b.png`, `arthur_a.png`: kontrollerte materialforhåndsvisninger, 900 × 700 piksler.
- `asset_audit.json`: geometri, materialer, teksturoppløsninger, skjelett og SHA-256-kontroll av originalfilene.
- `inspect_assets.py`: gjenskapbar lokal import og inspeksjon. Kjøres i en separat Blender-prosess.

Første produksjonstrinn er en referansebasert grunnmodell av Smithfield’s og den tilstøtende gaten. Detaljering av en hel by er et større prosjekt som bør bygges og vurderes område for område. Ingen produksjonstid er lovet før det første utsnittet er målt og kontrollert.
