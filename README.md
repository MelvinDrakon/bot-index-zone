# Bot Telegram Index Zone

Ce que fait le bot, toutes les 10 minutes :

- **Captures des bots** : tu envoies une capture (ou un album) au bot en privé, avec un texte si tu veux. Il la republie sur le canal avec le titre « Résultats des bots », la date et l'avertissement de risque, puis te confirme « Publié sur le canal ».
- **Posts programmés** (lundi → vendredi, heure de Paris) :
  - 09:00 : un post de la série Index Zone (10 posts qui tournent en boucle) + l'offre du guide PDF
  - 17:40 : rappel du live de 18h
  - 20:40 : rappel du live de 21h

Tout le texte se modifie dans `contenu.json`.

## Mise en route (10 minutes, une seule fois)

1. **Le bot admin du canal** : dans Telegram, canal → Administrateurs → Ajouter → ton bot, avec le droit « Publier des messages ».
2. **Ton ID** : envoie `/start` à ton bot. Il te répondra ton ID quand le bot tournera (étape 5). Fais pareil pour ton associé.
3. **Le token** : dans le dépôt GitHub → Settings → Secrets and variables → Actions → onglet *Secrets* → New secret : `BOT_TOKEN` = le token donné par BotFather. Ne le colle nulle part ailleurs.
4. **Les variables** : même page, onglet *Variables* :
   - `CHANNEL_ID` = `@nom_de_ton_canal` (ou l'ID `-100…` si le canal est privé)
   - `ADMIN_IDS` = vos IDs Telegram séparés par une virgule, ex. `123456789,987654321`
5. **Démarrer** : onglet Actions → « Bot Telegram Index Zone » → *Run workflow*. Ensuite il tourne seul toutes les 10 minutes.

## À remplacer dans `contenu.json`

- `[@TON_PSEUDO]` : le compte à qui écrire « INDEX » pour recevoir le PDF
- `[LIEN DU COMPTE TIKTOK]` : le lien de votre compte TikTok

## Bon à savoir

- Délai de publication d'une capture : 10 à 20 minutes (GitHub lance la tâche toutes les 10 min, parfois avec du retard).
- Seuls les IDs listés dans `ADMIN_IDS` peuvent faire publier quelque chose.
- `jours` dans le programme : 0 = lundi … 6 = dimanche.
