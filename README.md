# claude-starter

> Template Claude Code prêt à l'emploi pour démarrer n'importe quel projet en 2 minutes.

## Quickstart

**Étape 1 — Cloner dans ton projet**
```bash
git clone https://github.com/PetitPelican/claude-starter.git .
```

**Étape 2 — Recharger VS Code**

Après le clone, recharge la fenêtre pour que Claude Code détecte les nouveaux skills :

`Shift + Ctrl + P` → **Developer: Reload Window**

> Sans ce rechargement, `/agent-init` n'apparaît pas dans Claude Code.

**Étape 3 — Initialiser**

Lance dans Claude Code :
```
/agent-init
```

L'agent va scanner ton projet, te poser 5 questions, et configurer automatiquement :
- `CLAUDE.md` personnalisé pour ton projet
- Agents adaptés à ton type de projet (dev / data / API)
- Fichiers mémoire pré-remplis
- Skills caveman + memory-update prêts à l'emploi

**Étape 4 — Coder**

C'est tout. Lance `/memory-update` en fin de sprint pour maintenir la mémoire à jour.

---

## Projet existant

Si ton projet a déjà du code, ne clone pas dans le répertoire racine — copie uniquement le dossier `.claude/` :

```bash
# Cloner dans un dossier temporaire
git clone https://github.com/PetitPelican/claude-starter.git /tmp/claude-starter

# Copier uniquement .claude/ dans ton projet existant
cp -r /tmp/claude-starter/.claude ./

# Nettoyer
rm -rf /tmp/claude-starter
```

Sur Windows (PowerShell) :
```powershell
git clone https://github.com/PetitPelican/claude-starter.git $env:TEMP\claude-starter
Copy-Item -Recurse "$env:TEMP\claude-starter\.claude" ".\.claude"
Remove-Item -Recurse -Force "$env:TEMP\claude-starter"
```

Puis recharge VS Code (`Shift + Ctrl + P` → **Developer: Reload Window**) et lance `/agent-init`.

> `agent-init` détecte automatiquement que le projet est existant et ne touche pas à tes fichiers — il ajoute uniquement ce qui manque.

---

## Ce qui est inclus

### Agents disponibles

| Catégorie | Agents |
|---|---|
| Dev | frontend, backend, mobile, db, auth, payments |
| Data | sql, python, ingestion, transformation, orchestration |
| API | routes, auth, docs |
| Ops | build, qa, audit |

### Skills
- `caveman` — mode ultra-compressé (~75% moins de tokens)
- `caveman-compress` — compresse les fichiers mémoire
- `memory-update` — met à jour la mémoire du projet

### Mémoire
- `MEMORY.md` — index de tous les fichiers mémoire
- `state.md` — features faites / en cours / bloquées
- `decisions.md` — décisions d'architecture (le pourquoi)
- `architecture.md` — couches, flux de données, environnements (le quoi)
- `data-model.md` — modélisation des tables par couche (projets data/SaaS)
- `business.md` — règles métier, pricing, rôles
- `clients.md` — onboarding, trial, billing, résiliation

---

## Configuration MCP

Copier `.mcp.json.example` → `.mcp.json` et remplir avec tes clés.

## Permissions

Copier `.claude/settings.local.json.example` → `.claude/settings.local.json` et adapter.

---

## Contribuer

Les agents sont dans `.claude/agents/` — PR bienvenues pour améliorer les templates.
