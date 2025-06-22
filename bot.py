import os
import logging
import requests
import qrcode
from gtts import gTTS
from bardapi import BardCookies
from googletrans import Translator
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# === CONFIGURATION DU LOGGING ===
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# === CONFIGURATION DES CLÉS & VARIABLES ===
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # Assurez-vous de définir TELEGRAM_BOT_TOKEN dans vos variables d'environnement

cookies = {
    '__Secure-1PSID': os.getenv('__Secure-1PSID'),
    '__Secure-1PSIDTS': os.getenv('__Secure-1PSIDTS'),
    '__Secure-1PSIDCC': os.getenv('__Secure-1PSIDCC'),
}

bard = BardCookies(cookie_dict=cookies)
translator = Translator()

# === COMMANDES ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome = (
        "Bienvenue sur le bot **HMB - L'Assistant IA Ultime !**\n\n"
        "Je suis ici pour t'aider avec des traductions, infos météo, vidéos YouTube, IA Gemini, audio texte et bien plus encore !\n\n"
        "**Abonne-toi à notre chaîne officielle** pour des fichiers utiles, mises à jour et bonus :\n"
        "➡️ [Fichier HATunnel Plus](https://t.me/FichierHatunnelPlus)\n\n"
        "Tape /help pour voir tout ce que je peux faire pour toi !"
    )
    await update.message.reply_markdown(welcome)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """Commandes disponibles :

/start – Démarrer le bot  
/help – Afficher l'aide  
/whoami – Ton nom d'utilisateur  
/hmb – Infos sur HMB  
/ping – Vérifie si le bot est en ligne  
/generate_qr – Génère un QR code  
/translate fr Hello – Traduit le texte  
/weather Paris – Météo d'une ville  
/youtube [URL] – Télécharger audio YouTube  
/gemini [question] – Poser une question à Gemini  
/tts fr Bonjour – Voix audio  
/ip – Ton IP publique  
/crypto btc – Prix crypto (btc, eth, etc.)  
/define mot – Définition rapide  
/calc 2+2*3 – Calculatrice  
/langdetect texte – Détection de langue  
/shorten [lien] – Raccourcir un lien"""
    await update.message.reply_text(help_text)

async def whoami(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.from_user.username
    await update.message.reply_text(f"Ton nom d'utilisateur est @{username}")

async def hmb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("HMB est un assistant IA complet basé sur Google Gemini, disponible sur Telegram.")

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Pong ! Le bot est actif et fonctionne bien.")

async def generate_qr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        return await update.message.reply_text("Utilisation : /generate_qr [texte]")
    texte = ' '.join(context.args)
    img = qrcode.make(texte)
    file_path = "/tmp/qrcode.png"
    img.save(file_path)
    with open(file_path, 'rb') as qr_file:
        await update.message.reply_photo(qr_file)

async def translate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        return await update.message.reply_text("Utilisation : /translate fr Hello")
    dest = context.args[0]
    texte = ' '.join(context.args[1:])
    result = translator.translate(texte, dest=dest)
    await update.message.reply_text(result.text)

async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Utilisation : /weather Paris")
    city = ' '.join(context.args)
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return await update.message.reply_text("Clé API météo non configurée.")
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=fr"
    response = requests.get(url)
    if response.status_code != 200:
        return await update.message.reply_text("Ville introuvable.")
    data = response.json()
    desc = data['weather'][0].get('description', 'Non précisé')
    temp = data['main'].get('temp', 'N/A')
    await update.message.reply_text(f"Météo à {city} : {desc}, {temp}°C")

async def youtube(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Utilisation : /youtube [URL]")
    url = context.args[0]
    if '=' in url:
        vid_id = url.split('=')[-1]
    elif '/' in url:
        vid_id = url.split('/')[-1]
    else:
        return await update.message.reply_text("URL YouTube invalide.")
    await update.message.reply_text(f"Télécharge ici : https://api.vevioz.com/api/button/mp3/{vid_id}")

async def gemini_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Utilisation : /gemini [ta question]")
    message = ' '.join(context.args)
    try:
        rep = bard.get_answer(message)['content']
        await update.message.reply_text(rep)
    except Exception as e:
        logger.error(f"Erreur Gemini : {e}")
        await update.message.reply_text("Erreur avec Gemini.")

async def tts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        return await update.message.reply_text("Utilisation : /tts fr Bonjour")
    lang = context.args[0]
    texte = ' '.join(context.args[1:])
    audio = gTTS(text=texte, lang=lang)
    file_path = "/tmp/audio.mp3"
    audio.save(file_path)
    with open(file_path, 'rb') as f:
        await update.message.reply_audio(f)

async def ip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        ip = requests.get("https://api64.ipify.org").text
        await update.message.reply_text(f"Ton IP publique est : {ip}")
    except:
        await update.message.reply_text("Impossible d'obtenir l'adresse IP.")

async def crypto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Utilisation : /crypto btc")
    symbol = context.args[0].lower()
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies=usd"
    r = requests.get(url)
    if r.status_code != 200:
        return await update.message.reply_text("Erreur ou crypto introuvable.")
    price = r.json().get(symbol, {}).get('usd')
    if price:
        await update.message.reply_text(f"Prix actuel de {symbol.upper()} : ${price}")
    else:
        await update.message.reply_text("Crypto introuvable.")

async def define(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Utilisation : /define mot")
    word = context.args[0]
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    r = requests.get(url)
    if r.status_code != 200:
        return await update.message.reply_text("Mot introuvable.")
    try:
        definition = r.json()[0]["meanings"][0]["definitions"][0]["definition"]
        await update.message.reply_text(f"Définition de {word} : {definition}")
    except Exception:
        await update.message.reply_text("Erreur lors de l'extraction de la définition.")

async def calc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Utilisation : /calc 2+2")
    expr = ' '.join(context.args)
    try:
        result = eval(expr, {"__builtins__": None}, {})
        await update.message.reply_text(f"Résultat : {result}")
    except:
        await update.message.reply_text("Erreur dans le calcul.")

async def langdetect(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Utilisation : /langdetect texte")
    texte = ' '.join(context.args)
    lang = translator.detect(texte).lang
    await update.message.reply_text(f"Langue détectée : {lang}")

async def shorten(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Utilisation : /shorten [URL]")
    long_url = context.args[0]
    try:
        r = requests.get(f"https://is.gd/create.php?format=simple&url={long_url}")
        await update.message.reply_text(f"Lien raccourci : {r.text}")
    except:
        await update.message.reply_text("Erreur lors du raccourcissement.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.type in ["group", "supergroup"]:
        msg = update.message.text
        try:
            rep = bard.get_answer(msg)['content']
            await update.message.reply_text(rep)
        except Exception:
            await update.message.reply_text("Erreur IA.")

# === LANCEMENT DU BOT ===
def main():
    if not TOKEN:
        raise ValueError("Le token du bot Telegram n'est pas défini.")
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("whoami", whoami))
    app.add_handler(CommandHandler("hmb", hmb))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(CommandHandler("generate_qr", generate_qr))
    app.add_handler(CommandHandler("translate", translate))
    app.add_handler(CommandHandler("weather", weather))
    app.add_handler(CommandHandler("youtube", youtube))
    app.add_handler(CommandHandler("gemini", gemini_command))
    app.add_handler(CommandHandler("tts", tts))
    app.add_handler(CommandHandler("ip", ip))
    app.add_handler(CommandHandler("crypto", crypto))
    app.add_handler(CommandHandler("define", define))
    app.add_handler(CommandHandler("calc", calc))
    app.add_handler(CommandHandler("langdetect", langdetect))
    app.add_handler(CommandHandler("shorten", shorten))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()

if __name__ == "__main__":
    main()
