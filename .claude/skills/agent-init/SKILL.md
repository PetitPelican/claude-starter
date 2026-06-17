---
name: agent-init
description: >
  Initialise la structure Claude Code d'un nouveau projet à partir du repo claude-starter.
  Scanne tous types de fichiers, détecte la stack, suggère MCPs/CLIs, pose 6 questions,
  personnalise CLAUDE.md (rôle, règles adaptées), supprime les agents non pertinents,
  pré-remplit les fichiers mémoire.
  Trigger: /agent-init ou "initialise ce projet"
---

# Agent Init

## Prérequis

Le dossier `.claude/` doit être présent dans le projet.

**Nouveau projet (répertoire vide) :**
```bash
git clone https://github.com/PetitPelican/claude-starter.git .
```

**Projet existant (code déjà présent) :**
```bash
# Linux / Mac
git clone https://github.com/PetitPelican/claude-starter.git /tmp/claude-starter
cp -r /tmp/claude-starter/.claude ./
rm -rf /tmp/claude-starter

# Windows PowerShell
git clone https://github.com/PetitPelican/claude-starter.git $env:TEMP\claude-starter
Copy-Item -Recurse "$env:TEMP\claude-starter\.claude" ".\.claude"
Remove-Item -Recurse -Force "$env:TEMP\claude-starter"
```

Si `.claude/` est absent, affiche ces instructions et arrête.

---

## Détection du contexte

Avant de démarrer, détecte si c'est un projet nouveau ou existant :
- **Projet existant** : présence de fichiers de code (`src/`, `app/`, `*.py`, `*.ts`, etc.) OU d'un historique git (`git log` retourne des commits)
- **Nouveau projet** : répertoire quasi-vide (uniquement `.claude/`, `CLAUDE.md`, `.gitignore`, `README.md`)

En mode **projet existant** :
- Ne pas modifier les fichiers qui existent déjà hors de `.claude/`
- Ne pas écraser un `CLAUDE.md` déjà personnalisé (vérifier si `[PROJECT_NAME]` est encore présent)
- Pour les fichiers mémoire : ne créer que ceux qui n'existent pas encore
- Signaler à l'utilisateur ce qui existait déjà vs ce qui a été ajouté

---

## Phase 1 — Scan automatique

Lis **tout** ce que tu trouves dans le répertoire courant. Ne te limite pas aux fichiers code.

### Fichiers de config / stack
- `package.json`, `requirements.txt`, `go.mod`, `pyproject.toml`, `Cargo.toml`, `pom.xml`, `build.gradle`
- `dbt_project.yml`, `airflow.cfg`, `prefect.yaml`, `dagster.yaml`
- `docker-compose.yml`, `Dockerfile`, `kubernetes/`, `.github/workflows/`
- `.mcp.json` — MCPs déjà configurés
- `.env.example` — variables d'environnement déclarées

### Fichiers de documentation & métier
Lis tout fichier lisible qui décrit le projet : README, specs, cahiers des charges, business plans, PRDs, wireframes décrits en texte.
- `.md`, `.txt`, `.rst` — lecture directe
- Tout fichier dont le nom contient : `spec`, `brief`, `cahier`, `requirements`, `roadmap`, `business`

**Fichiers binaires — procédure d'extraction obligatoire :**

Pour chaque fichier `.docx` trouvé, tente dans l'ordre :
```bash
# Option 1 — pandoc (le plus fiable)
pandoc "<fichier>" -t plain --wrap=none

# Option 2 — python-docx
python -c "import docx; print('\n'.join([p.text for p in docx.Document('<fichier>').paragraphs]))"

# Option 3 — docx2txt
docx2txt "<fichier>" -

# Option 4 — LibreOffice
soffice --headless --convert-to txt "<fichier>" --outdir /tmp && cat /tmp/<nom>.txt
```
Si aucune option ne fonctionne, affiche : "Fichier `<nom>.docx` non extractible — résume-moi son contenu en quelques phrases." et attends la réponse avant de continuer.

Pour chaque fichier `.pdf` trouvé, tente dans l'ordre :
```bash
# Option 1 — pdftotext (poppler)
pdftotext "<fichier>" -

# Option 2 — python pdfminer
python -c "from pdfminer.high_level import extract_text; print(extract_text('<fichier>'))"

# Option 3 — pymupdf
python -c "import fitz; doc=fitz.open('<fichier>'); print('\n'.join([p.get_text() for p in doc]))"
```
Si aucune option ne fonctionne : "Fichier `<nom>.pdf` non extractible — résume-moi son contenu en quelques phrases."

Pour chaque fichier `.xlsx` ou `.csv` trouvé, tente :
```bash
# CSV — lecture directe (premiers 50 lignes)
head -50 "<fichier>"

# XLSX — python openpyxl
python -c "import openpyxl; wb=openpyxl.load_workbook('<fichier>'); [print(row) for sheet in wb.sheetnames for row in wb[sheet].iter_rows(values_only=True, max_row=20)]"
```

**Règle** : ne passe pas au rapport de scan tant qu'un fichier métier extractible n'a pas été lu. Les fichiers métier sont prioritaires sur les fichiers de code pour comprendre le projet.

### CLIs installés
Vérifie la présence de chaque CLI via `command -v` (ou `where` sur Windows) :
`git`, `vercel`, `eas`, `supabase`, `stripe`, `dbt`, `kubectl`, `helm`, `terraform`, `aws`, `gcloud`, `az`, `snowflake`, `airbyte`, `prefect`, `dagster`, `poetry`, `conda`

### Rapport de scan
Synthétise en une liste courte :
- Stack détectée (frameworks, langages, BDD, cloud)
- Services externes identifiés (Supabase, Snowflake, Stripe, S3, etc.)
- CLIs présents
- MCPs déjà configurés
- Ce que tu as compris du projet (en 2-3 phrases max)

---

## Phase 2 — Questions (6)

Pose chaque question une par une. Attends la réponse avant de continuer.

**Q1 — Nom et description**
"Quel est le nom de ce projet et en une phrase, qu'est-ce qu'il fait ?"

**Q2 — Rôle de Claude**
"Dans ce projet, quel rôle dois-je jouer ?" Propose des options selon le scan :
- CTO / Tech Lead (projets produit, SaaS, fullstack)
- Data Engineer / Architecte data (projets pipeline, warehouse)
- Lead Data Scientist (projets ML, analyse)
- Développeur senior (projet sans dimension produit)
- Assistant technique (projet sans décision d'archi à déléguer)
- Autre → laisser l'utilisateur décrire librement

**Q3 — Type de projet**
"Quel est le type de projet ?" Présente uniquement les options cohérentes avec le scan :
- Web app (frontend + backend)
- Mobile app
- Fullstack web + mobile
- API backend
- SaaS multi-tenant
- Data pipeline / ETL
- Data science / ML
- Data warehouse / Analytics
- Script / automatisation

**Q4 — Domaines actifs**
"Quels domaines sont actifs dans ce projet ?" (plusieurs réponses) :
`frontend` · `backend` · `mobile` · `base de données` · `authentification` · `paiements` · `data pipeline` · `SQL/warehouse` · `Python/ML` · `orchestration` · `API routes` · `documentation API`

**Q5 — Outils**
Basé sur le scan, liste les services/MCPs/CLIs **détectés** et demande confirmation + ce qui manque :
"J'ai détecté [X, Y, Z]. Est-ce complet ? Y a-t-il d'autres outils à configurer ?"

Référence de MCPs disponibles selon les services détectés :
| Service détecté | MCP à suggérer |
|---|---|
| Supabase | `@supabase/mcp-server-supabase` |
| Stripe | `@stripe/mcp` |
| Notion | `@notionhq/notion-mcp-server` |
| Snowflake | `@modelcontextprotocol/server-snowflake` |
| PostgreSQL direct | `@modelcontextprotocol/server-postgres` |
| GitHub | `@modelcontextprotocol/server-github` |
| Slack | `@modelcontextprotocol/server-slack` |
| AWS | `mcp-server-aws` |
| Linear | `@linear/mcp-server` |
| Jira | `@modelcontextprotocol/server-jira` |

Si un service est détecté mais son MCP n'est pas dans `.mcp.json`, suggère-le explicitement avec la commande d'installation.

**Q6 — Contraintes**
"Y a-t-il des contraintes spécifiques ?" (plusieurs réponses) :
`multi-tenant` · `RBAC strict` · `conformité RGPD` · `conformité SOC2` · `budget infra limité` · `pas de git` · `pas d'IA dans le produit` · `déploiement on-premise` · `autre`

---

## Phase 3 — Personnalisation

### CLAUDE.md

**Section Rôle** — remplacer :
- `[PROJECT_NAME]` → nom du projet
- `[ROLE]` → rôle choisi en Q2, adapté :
  - CTO/Tech Lead → "tu es le CTO/Tech Lead de **[PROJECT_NAME]**"
  - Data Engineer → "tu es le Data Engineer / Architecte data de **[PROJECT_NAME]**"
  - Data Scientist → "tu es le Lead Data Scientist de **[PROJECT_NAME]**"
  - Autre → reformuler selon la réponse libre
- `[DESCRIPTION_1_PHRASE]` → description fournie
- `[STACK]` → stack détectée + confirmée
- Phase actuelle → adapter selon le contexte détecté

**Section Règles** — sélectionner uniquement les règles pertinentes :

| Règle | Inclure si |
|---|---|
| Git (commit/push sur demande) | `git` détecté dans CLIs ET projet versionné |
| TypeScript strict | TypeScript détecté dans la stack |
| Zéro valeur hardcodée CSS | Frontend web détecté |
| Python strict (mypy/pyright) | Python détecté, pas de TS |
| Pas de print() / logging structuré | Python détecté |
| Idempotence pipelines | Data pipeline confirmé (Q4) |
| RLS / RBAC côté serveur | Multi-tenant ou RBAC strict (Q6) |
| Clés restreintes en prod | Paiements confirmés (Q4) |

Ne pas inclure une règle si elle ne s'applique pas au projet. Ne pas laisser les règles avec "(supprimer si non applicable)".

**Section Outils** — remplir avec les outils confirmés en Q5 uniquement. Si MCP suggéré mais pas encore installé, le lister avec la mention `(à installer)`.

### Agents

En fonction des domaines confirmés (Q4), **supprimer** les agents non pertinents :

| Domaine NON confirmé | Fichier à supprimer |
|---|---|
| Pas de frontend web | `agents/dev/agent-frontend.md` |
| Pas de mobile | `agents/dev/agent-mobile.md` |
| Pas de paiements | `agents/dev/agent-payments.md` |
| Pas de SQL/warehouse | `agents/data/agent-sql.md` |
| Pas de Python/ML | `agents/data/agent-python.md` |
| Pas de pipeline | `agents/data/agent-ingestion.md`, `agent-transformation.md`, `agent-orchestration.md` |
| Pas d'API routes | `agents/api/agent-routes.md`, `agents/api/agent-auth.md` |
| Pas de doc API | `agents/api/agent-docs.md` |
| Pas de data du tout | `agents/data/` (tout le dossier) |
| Pas de dev du tout | `agents/dev/` (tout le dossier) |
| Pas d'API du tout | `agents/api/` (tout le dossier) |

Toujours conserver : `agents/ops/`, `agents/audit/`

Après suppression, **compléter le contenu** des agents conservés :
- Remplacer `[FRONTEND_PATH]`, `[BACKEND_PATH]`, `[MOBILE_PATH]`, `[DB_PATH]` par les vrais chemins détectés dans le scan
- Compléter `## Stack` avec la stack réelle

### Memory

- `state.md` : remplacer `[PROJECT_NAME]` + date du jour
- `decisions.md` : remplacer `[PROJECT_NAME]` + pré-remplir la table Stack avec ce qui a été détecté dans le scan
- `business.md` : remplacer `[PROJECT_NAME]` + remplir les contraintes fournies en Q6 + rôles si mentionnés
- `clients.md` : conserver uniquement si paiements confirmés en Q4 ; sinon supprimer
- `data-model.md` : conserver uniquement si SQL/warehouse ou data pipeline confirmé en Q4 ; pré-remplir les couches pertinentes selon le type de projet (ex: raw/staging/marts pour un data warehouse, schema public uniquement pour un SaaS PostgreSQL) ; supprimer les couches non utilisées
- `architecture.md` : remplacer `[PROJECT_NAME]` + pré-remplir avec ce qui a été détecté dans le scan :
  - Section **Sources & ingestion** → fichiers de config source détectés (connecteurs, APIs, webhooks)
  - Section **Traitement / pipeline** → outils détectés (dbt, Airflow, ADF, scripts Python, etc.)
  - Section **Stockage** → BDD détectées (Snowflake, PostgreSQL, Supabase, S3, etc.)
  - Section **API / backend** → frameworks backend détectés
  - Section **Frontend / dataviz** → frameworks frontend détectés (Next.js, Power BI, Expo, etc.)
  - Section **Flux de données** → remplir le schéma `SOURCE → TRAITEMENT → STOCKAGE → API → FRONTEND` avec les vrais noms
  - Laisser vide les couches non détectées plutôt que de deviner
- `MEMORY.md` : remplacer `[PROJECT_NAME]` + ajouter une ligne pour `clients.md` si le fichier a été conservé

### MCPs non installés

Pour chaque MCP suggéré mais absent de `.mcp.json`, générer le bloc JSON à ajouter et afficher la commande d'installation.

---

## Phase 4 — Bypass des permissions

Vérifie et corrige les permissions pour éviter les prompts d'approbation à chaque action.

### `settings.local.json` (projet)
Vérifie que `.claude/settings.local.json` contient `"defaultMode": "bypassPermissions"` dans `permissions`.
- Si absent : l'ajouter
- Si le fichier n'existe pas : le créer avec ce contenu minimal :
```json
{
  "permissions": {
    "defaultMode": "bypassPermissions"
  }
}
```

### `~/.claude/settings.json` (global)
Vérifie que le fichier global contient aussi `"defaultMode": "bypassPermissions"`.
- Si absent : proposer à l'utilisateur de l'ajouter (action sur le fichier global — demander confirmation)
- Si le fichier n'existe pas : proposer de le créer

**Important :** après toute modification de settings, indiquer à l'utilisateur de faire `Shift+Ctrl+P` → **Developer: Reload Window** pour que les changements prennent effet.

---

## Résumé de fin

En fin d'init, afficher :
1. Ce qui a été personnalisé (CLAUDE.md, agents supprimés, memory pré-remplie)
2. MCPs à installer (commandes exactes)
3. Prochaine action recommandée (`/memory-update` pour valider l'état initial)

---

## Règles d'exécution

- Ne pas modifier les skills (`caveman/`, `caveman-compress/`, `memory-update.md`)
- Ne pas modifier `settings.json`
- Toujours confirmer les suppressions d'agents avant d'exécuter (liste + confirmation unique)
- Si un fichier n'est pas lisible (Excel, PDF) et qu'aucun outil n'est disponible, le signaler et continuer
