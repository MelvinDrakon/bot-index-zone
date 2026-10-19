"""Bot Telegram Index Zone : republie les captures des bots et poste le contenu programmé.

Tourne toutes les 10 minutes (GitHub Actions). Aucune dépendance externe.
Variables d'environnement :
  BOT_TOKEN   token donné par BotFather (secret GitHub)
  CHANNEL_ID  @nom_du_canal ou -100xxxxxxxxxx
  ADMIN_IDS   IDs Telegram autorisés à envoyer des captures, séparés par des virgules
"""
import json
import os
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
TZ = ZoneInfo("Europe/Paris")
TOKEN = os.environ.get("BOT_TOKEN", "")
CHANNEL = os.environ.get("CHANNEL_ID", "")
ADMINS = {int(x) for x in os.environ.get("ADMIN_IDS", "").replace(" ", "").split(",") if x}
API = f"https://api.telegram.org/bot{TOKEN}/"
STATE_FILE = os.path.join(HERE, "state.json")
CONTENT_FILE = os.path.join(HERE, "contenu.json")


def api(method, **params):
    data = urllib.parse.urlencode(
        {k: (json.dumps(v) if isinstance(v, (list, dict)) else v) for k, v in params.items()}
    ).encode()
    with urllib.request.urlopen(urllib.request.Request(API + method, data=data), timeout=30) as r:
        res = json.load(r)
    if not res.get("ok"):
        raise RuntimeError(f"{method}: {res}")
    return res["result"]


def load(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return default


def save(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def jour_fr(d):
    jours = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
    mois = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
            "août", "septembre", "octobre", "novembre", "décembre"]
    return f"{jours[d.weekday()]} {d.day} {mois[d.month - 1]}"


# ---------- 1. Captures envoyées au bot -> canal ----------

def legende_resultats(texte, content):
    now = datetime.now(TZ)
    lignes = [f"<b>{content['resultats']['titre']}</b> · {jour_fr(now)}"]
    if texte:
        lignes += ["", texte.strip()]
    lignes += ["", f"<i>{content['resultats']['avertissement']}</i>"]
    return "\n".join(lignes)


def traiter_messages(content):
    updates = api("getUpdates", timeout=0, allowed_updates=["message"])
    if not updates:
        return
    albums = {}
    for u in updates:
        m = u.get("message")
        if not m:
            continue
        uid = m["from"]["id"]
        chat = m["chat"]["id"]
        texte = m.get("caption") or m.get("text") or ""
        if texte.startswith("/start") or texte.startswith("/id"):
            api("sendMessage", chat_id=chat, text=f"Ton ID Telegram : {uid}")
            continue
        if uid not in ADMINS:
            continue
        photo = m["photo"][-1]["file_id"] if m.get("photo") else None
        if not photo and m.get("document", {}).get("mime_type", "").startswith("image/"):
            photo = m["document"]["file_id"]
        if not photo:
            continue
        if m.get("media_group_id"):
            albums.setdefault(m["media_group_id"], {"chat": chat, "photos": [], "texte": ""})
            albums[m["media_group_id"]]["photos"].append(photo)
            if texte:
                albums[m["media_group_id"]]["texte"] = texte
        else:
            api("sendPhoto", chat_id=CHANNEL, photo=photo,
                caption=legende_resultats(texte, content), parse_mode="HTML")
            api("sendMessage", chat_id=chat, text="Publié sur le canal.")
    for a in albums.values():
        media = [{"type": "photo", "media": p} for p in a["photos"][:10]]
        media[0]["caption"] = legende_resultats(a["texte"], content)
        media[0]["parse_mode"] = "HTML"
        api("sendMediaGroup", chat_id=CHANNEL, media=media)
        api("sendMessage", chat_id=a["chat"], text=f"Album de {len(media)} captures publié sur le canal.")
    # confirme les messages lus pour ne pas les retraiter
    api("getUpdates", offset=updates[-1]["update_id"] + 1, timeout=0)


# ---------- 2. Posts programmés ----------

def posts_programmes(content, state):
    now = datetime.now(TZ)
    today = now.date().isoformat()
    sent = state.setdefault("envoye", {})
    for slot in content["programme"]:
        if now.weekday() not in slot["jours"]:
            continue
        h, mi = map(int, slot["heure"].split(":"))
        start = now.replace(hour=h, minute=mi, second=0, microsecond=0)
        # fenêtre de 90 min : GitHub peut lancer la tâche avec du retard
        if not (start <= now < start + timedelta(minutes=90)):
            continue
        if sent.get(slot["id"]) == today:
            continue
        if slot["type"] == "index_zone":
            serie = content["index_zone"]
            i = state.get("index_zone_suivant", 0) % len(serie)
            texte = serie[i] + "\n\n" + content["appel_pdf"]
            state["index_zone_suivant"] = i + 1
        else:
            texte = slot["texte"]
        api("sendMessage", chat_id=CHANNEL, text=texte, parse_mode="HTML",
            disable_web_page_preview=True)
        sent[slot["id"]] = today


def main():
    if not TOKEN or not CHANNEL:
        print("BOT_TOKEN ou CHANNEL_ID manquant : configure-les dans GitHub (voir README).")
        return
    content = load(CONTENT_FILE, {})
    state = load(STATE_FILE, {})
    traiter_messages(content)
    posts_programmes(content, state)
    save(STATE_FILE, state)


if __name__ == "__main__":
    main()
