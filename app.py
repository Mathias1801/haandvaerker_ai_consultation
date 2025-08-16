import streamlit as st
import re
import json
import google.generativeai as genai
import os

# --- Konfiguration af API-nøgle fra GitHub Secrets ---
GENMI_API_KEY = st.secrets["GENMI_API_KEY"]
genai.configure(api_key=GENMI_API_KEY)

# === EMOTIONELLE KUNDETYPER ===
emotionelle_kundetyper = {
    "rød": (
        "Den røde kundetype drives af et behov for at bryde rutiner og finde ny energi gennem spændende, anderledes "
        "oplevelser. Kedsomhed skaber en indre uro, der leder dem mod løsninger, der giver et 'kick' og skiller sig ud. "
        "De er impulsive, nysgerrige og åbne for koncepter, der lover variation, overraskelser og unikke oplevelser. "
        "De værdsætter rejsen lige så højt som resultatet og vender kun tilbage, hvis de oplever, at der fortsat er "
        "ny inspiration og energi at hente."
    ),
    "gul": (
        "Den gule kundetype søger fællesskab, samhørighed og følelsen af at være en del af noget større. "
        "De tiltrækkes af varme, inkluderende miljøer, hvor relationer er i centrum, og hvor de føler sig set og hørt. "
        "Historier, personlighed og menneskelig kontakt har stor betydning, og de er loyale, hvis de oplever ægte "
        "forbindelse til brandet. Manglende opmærksomhed på deres behov for relation kan hurtigt gøre oplevelsen kold "
        "og uvedkommende for dem."
    ),
    "blå": (
        "Den blå kundetype motiveres af at genvinde struktur og kontrol, særligt i situationer præget af "
        "uklarhed eller usikkerhed. De foretrækker klare processer, detaljeret information og dokumentation, "
        "så de kan træffe beslutninger på et velinformeret grundlag. Gennemsigtighed, præcision og forudsigelighed "
        "er nøglen til deres tillid. Hvis processerne bryder sammen eller uforudsete problemer opstår uden forklaring, "
        "kan tilliden være svær at genopbygge."
    ),
    "grøn": (
        "Den grønne kundetype søger tryghed og stabilitet for at modvirke utryghed og usikkerhed. "
        "De vælger helst velafprøvede løsninger og pålidelige leverandører, der kan dokumentere erfaring "
        "og gode resultater. Kommunikation, der signalerer stabilitet, kontinuitet og sikkerhed, taler til dem. "
        "Når de først opnår tillid, er de ofte meget loyale, men selv små tegn på usikkerhed kan gøre dem tøvende."
    )
}

# === REGIONALE INDSIGTER ===
region_emo_insight = {
    "Hovedstaden": {
        "Storby": {
            "beskrivelse": (
                "I storbyerne er der høj digital tilstedeværelse, og forbrugerne laver omfattende online research før køb. "
                "De er meget modtagelige for visuel og video-baseret markedsføring og søger brands med stærk identitet "
                "og bæredygtighedsprofil. Impulskøb foregår ofte online eller via mobile betalingsløsninger, og de er hurtige "
                "til at reagere på nye trends og koncepter."
            ),
            "mest_udbredte_kundetype": ["rød", "gul"]
        },
        "By": {
            "beskrivelse": (
                "I de mindre byer er forbrugerne mere prisbevidste end i storbyen, men stadig digitalt aktive. "
                "Lokale kampagner og events skaber god respons, og der er en høj grad af loyalitet over for kendte brands, "
                "især hvis de har lokal tilstedeværelse og er relevante for det nære miljø."
            ),
            "mest_udbredte_kundetype": ["blå", "gul"]
        },
        "Opland": {
            "beskrivelse": (
                "I oplandet er købsadfærden mere relationsbaseret, og tillid til brand bygges gennem personlige anbefalinger "
                "og god service. Der er mindre tilbøjelighed til at afprøve helt nye brands uden social bekræftelse, "
                "og beslutningsprocessen kan være mere langsom og forsigtig."
            ),
            "mest_udbredte_kundetype": ["grøn"]
        }
    },
    "Sjælland": {
        "Storby": {
            "beskrivelse": (
                "Storbyerne i Region Sjælland kombinerer storbyforbrug med stærk regional tilknytning. "
                "Forbrugerne er villige til at betale ekstra for kvalitet, især inden for mad, bolig og oplevelser. "
                "Kampagner med tydelig lokal identitet skaber høj engagement."
            ),
            "mest_udbredte_kundetype": ["gul", "blå"]
        },
        "By": {
            "beskrivelse": (
                "I de mindre byer er brandloyaliteten høj, og praktiske tilbud med klare fordele værdsættes. "
                "Kampagner med fællesskabstema eller lokale ambassadører fungerer særligt godt, "
                "da de styrker tilknytningen til brandet."
            ),
            "mest_udbredte_kundetype": ["blå"]
        },
        "Opland": {
            "beskrivelse": (
                "Oplandet har et mere traditionelt købs- og medieforbrug, men brugen af sociale medier er stigende. "
                "Mund-til-mund anbefalinger via lokale netværk er fortsat en af de stærkeste drivkræfter bag købsbeslutninger."
            ),
            "mest_udbredte_kundetype": ["grøn"]
        }
    },
    "Syddanmark": {
        "Storby": {
            "beskrivelse": (
                "I storbyerne balancerer forbrugerne mellem pris og kvalitet. "
                "Personlige kampagner og storytelling skaber god respons, "
                "og sociale medier spiller en central rolle i opdagelsen af nye produkter."
            ),
            "mest_udbredte_kundetype": ["gul", "blå"]
        },
        "By": {
            "beskrivelse": (
                "Mindre byer har en praktisk orienteret købsadfærd med fokus på klare prisfordele og lokal tilstedeværelse. "
                "Loyalitetsprogrammer modtages positivt og kan fastholde kunder over længere tid."
            ),
            "mest_udbredte_kundetype": ["blå"]
        },
        "Opland": {
            "beskrivelse": (
                "Oplandets forbrugere har en traditionel tilgang, men viser stigende interesse for e-handel, "
                "særligt inden for nicheprodukter. Tillid og personlige relationer er afgørende for køb."
            ),
            "mest_udbredte_kundetype": ["grøn"]
        }
    },
    "Midtjylland": {
        "Storby": {
            "beskrivelse": (
                "Storbysegmentet er innovativt og trendsøgende med hurtig adoption af nye koncepter og platforme. "
                "Interaktive kampagner og influencer-samarbejder skaber høj engagement og kan accelerere produktlanceringer."
            ),
            "mest_udbredte_kundetype": ["rød", "gul"]
        },
        "By": {
            "beskrivelse": (
                "I de mindre byer kombineres lokal forankring med interesse for nationale trends. "
                "Kampagner, der forener funktionalitet med social værdi, opfattes som relevante og værdiskabende."
            ),
            "mest_udbredte_kundetype": ["gul", "blå"]
        },
        "Opland": {
            "beskrivelse": (
                "Oplandet lægger stor vægt på personlige relationer og lokale anbefalinger i købsprocessen. "
                "Praktiske løsninger prioriteres, og tillidsopbygning er en central del af salgsarbejdet."
            ),
            "mest_udbredte_kundetype": ["grøn"]
        }
    },
    "Nordjylland": {
        "Storby": {
            "beskrivelse": (
                "I storbyerne værdsættes autenticitet og direkte kommunikation. "
                "Oplevelsesbaserede kampagner og branding, der fremmer fællesskab, skaber stærk respons."
            ),
            "mest_udbredte_kundetype": ["gul", "grøn"]
        },
        "By": {
            "beskrivelse": (
                "Mindre byer har en stærk lokal identitet og høj loyalitet over for kendte brands. "
                "En kombination af offline events og online markedsføring har vist sig effektiv."
            ),
            "mest_udbredte_kundetype": ["blå", "grøn"]
        },
        "Opland": {
            "beskrivelse": (
                "Oplandet er meget tillidsorienteret, og købsbeslutninger træffes ofte efter længere overvejelse. "
                "Lokale netværk og personlige relationer spiller en afgørende rolle for salget."
            ),
            "mest_udbredte_kundetype": ["grøn"]
        }
    }
}

# === Håndværkerprofil (eksempel) ===
handvaerker = {
    "navn": "Mikkel Andersen",
    "fag": "tømrer",
    "værdier": ["kvalitet", "troværdighed", "lokalt kendskab"],
    "lokation": "Aalborg",
    "stil": "lavpraktisk, ærlig og jordnær"
}

# === Streamlit UI ===
st.title("Personlig beskedgenerator til kunder")

# Inputfelter
kunde_navn = st.text_input("Kundenavn", "Markus Mandal Thøgersen")
kunde_adresse = st.text_input("Adresse", "Vestvej 12")
kunde_opgave = st.text_input("Opgave", "nyt spisebord i eg")
kunde_by = st.text_input("By", "Langholt")
kunde_alder = st.number_input("Alder", min_value=0, max_value=120, value=32)
kunde_boligtype = st.text_input("Boligtype", "Rækkehus")
kunde_jobtitel = st.text_input("Jobtitel", "IT-konsulent")

kunde = {
    "navn": kunde_navn,
    "adresse": kunde_adresse,
    "opgave": kunde_opgave,
    "by": kunde_by,
    "alder": kunde_alder,
    "boligtype": kunde_boligtype,
    "jobtitel": kunde_jobtitel
}

# Funktioner til kundeprofil
def kundeprofil_summary(kunde):
    summary = f"Navn: {kunde.get('navn')}\nAdresse: {kunde.get('adresse')}\nOpgave: {kunde.get('opgave')}"
    if kunde.get("by"): summary += f"\nBy: {kunde['by']}"
    if kunde.get("alder"): summary += f"\nAlder: {kunde['alder']}"
    if kunde.get("boligtype"): summary += f"\nBoligtype: {kunde['boligtype']}"
    if kunde.get("jobtitel"): summary += f"\nJobtitel: {kunde['jobtitel']}"
    return summary

def find_region_emo_insight(kunde):
    prompt = f"""
    Du får en kundeprofil med en adresse og by. 
    Identificér hvilken dansk region og kategori (storby, by, opland).
    Returnér kun i JSON med nøglerne: region og kategori.
    Kunde: {kunde}
    """
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    text = response.text.strip()
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError(f"Kunne ikke finde JSON i output: {text}")
    result = json.loads(match.group())
    region = result["region"]
    kategori = result["kategori"]
    info = region_emo_insight[region][kategori]
    prim_kundetype = info["mest_udbredte_kundetype"][0]
    return info["beskrivelse"], prim_kundetype, emotionelle_kundetyper[prim_kundetype]

def generer_besked(handvaerker, kunde):
    regional_tekst, prim_kundetype, kundetype_tekst = find_region_emo_insight(kunde)
    prompt = f"""
    Du er en dansk {handvaerker['fag']}, der skal skrive en personlig besked til kunden.
    Kundeoplysninger:
    {kundeprofil_summary(kunde)}
    Regionale indsigter: {regional_tekst}
    Primær kundetype: {prim_kundetype}
    Kendetegn: {kundetype_tekst}
    Skriv en venlig besked (maks. 8 linjer).
    """
    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(prompt)
    return response.text.strip()

# Knap til generering
if st.button("Generer besked"):
    with st.spinner("Genererer besked..."):
        besked = generer_besked(handvaerker, kunde)
        st.success("Besked genereret!")
        st.text_area("Personlig besked", besked, height=200)
