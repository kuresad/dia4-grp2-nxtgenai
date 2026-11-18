# TD 1 : cinq modèles, vingt questions (21 octobre 2026)

Livrables du TD 1. Les chemins écrits *dans* les fichiers (`source_file` des traces, `trace_file` de la
comparaison, par exemple `traces-raw/state-A.jsonl`) sont relatifs à ce dossier `td1/`. Le code du kit et
la base qui les ont produits sont à la [racine du dépôt](../README.md).

## Livrables

| Livrable | Fichier | État |
|---|---|---|
| Vingt références, requête et valeur | [`reference-td1.csv`](reference-td1.csv) | Fait à l'étape 1 ; revérifiées en SQL et par un recalcul Python indépendant, les 20 concordent ([note](notes/reference-checks-td1.md)) |
| Toutes les tentatives, tous les runs | [`traces-td1.csv`](traces-td1.csv), [`traces-td1.jsonl`](traces-td1.jsonl) | 319 tentatives, 11 runs, toutes `nature = real` ; le JSONL contient les mêmes lignes que le CSV, au format d'état du skeleton |
| Lot de base seul (100 cellules) | [`traces-td1-base.csv`](traces-td1-base.csv), [`traces-td1-base.jsonl`](traces-td1-base.jsonl) | 106 tentatives : 100 premières tentatives + 6 retry après HTTP 429 (les lignes de `traces-td1.csv` avec `in_base_batch = yes`) |
| Fichiers bruts de chaque opérateur | [`traces-raw/`](traces-raw/) | Conservés sans modification |
| Une ligne finale par modèle × question | [`model-question-comparison-en_J.csv`](model-question-comparison-en_J.csv) | 100 lignes du lot de base, cause de chaque échec dans `explanation` ; [`model-question-comparison-en_R.csv`](model-question-comparison-en_R.csv) est la version antérieure, construite sur `FULL-1` seul |
| Vue croisée modèles × questions | [`notes/pivot-td1.md`](notes/pivot-td1.md) | Générée depuis la comparaison ; contient aussi chaque run et les cellules qui changent d'un run à l'autre |
| Synthèse des cinq modèles | [`five-model-summary-en.csv`](five-model-summary-en.csv) | Indice, prix datés ou N/A avec raison, accès, résultats par famille |
| Prompts tels qu'utilisés | [`prompts-en.md`](prompts-en.md) | Une seule version, inchangée au TD 2 (empreintes vérifiées) |
| Rapport de séance | `../reports/td1.md` | **Manquant** : à écrire par le groupe |

## Les runs

Tous les runs ont utilisé le même prompt (même empreinte par question), les mêmes références et les
paramètres du kit. Le lot de base suit la répartition A à E du protocole, un run par modèle. Les autres runs
sont des répétitions, chacune lancée avec ses propres fichiers `--state`/`--out` : ce sont des expériences
distinctes, jamais comptées comme des retry.

| run_id | Opérateur | Modèle | Fichier brut | Début (UTC) | Lot de base |
|---|---|---|---|---|---|
| `FULL-1` | Enzo | les cinq modèles en un seul `--run` | `traces-raw/traces-td1_full.csv` | 2026-10-21 13:50 | oui pour E (Dots) seulement |
| `A-jason-1` | Jason (A) | `groq:openai/gpt-oss-120b` | `traces-raw/state-A.jsonl` | 14:12 | oui |
| `B-1` | Yohan (B) | `groq:openai/gpt-oss-20b` | `traces-raw/traces-B.csv` | 14:14 | oui |
| `D-kuresa-1` | Kuresa (D) | `groq:qwen/qwen3.8-27b` | `traces-raw/state-D-Kuresa.jsonl` | 14:17 | oui |
| `D-paul-1` | Paul | `groq:qwen/qwen3.8-27b` | `traces-raw/state-D-Paul.jsonl` | 14:17 | répétition |
| `A-op2-1` | Kuresa | `groq:openai/gpt-oss-120b` | `traces-raw/trace_A.csv` | 14:20 | répétition |
| `A-jason-2` | Jason | `groq:openai/gpt-oss-120b` | `traces-raw/state-A_2.jsonl` | 14:31 | répétition |
| `D-paul-2` | Paul | `groq:qwen/qwen3.8-27b` | `traces-raw/state-D_2-Paul.jsonl` | 14:32 | répétition |
| `D-kuresa-2` | Kuresa | `groq:qwen/qwen3.8-27b` | `traces-raw/state-D-Kuresa2.jsonl` | 14:35 | répétition |
| `C-jason-1` | Florent | `openrouter:cohere/north-mini-code:free` | `traces-raw/state-C.jsonl` | 14:37 | oui |
| `E-jason-1` | Jason | `openrouter:dots-studio/dots-3-note-preview:free` | `traces-raw/state-E-Jason.jsonl` | 19:18 | répétition |

Les retry (HTTP 429) de ces runs sont analysés au TD 2 :
[`../td2/A-quorum/results/retries.md`](../td2/A-quorum/results/retries.md).

## Commandes de rejeu (depuis la racine du dépôt)

```bash
python verify-data.py                          # empreintes de la base et des CSV, "ok": true
python check_access.py --no-network            # Python, empreintes de la base et des CSV, aucun appel aux modèles
python skeleton-multi-llm-en.py --rates --state td1/traces-td1-base.jsonl --reference td1/reference-td1.csv
```

Ces commandes ne font aucun appel réseau. Un nouveau run d'un modèle (inutile pour les TD 2 et 3) se lance
ainsi :

```bash
python skeleton-multi-llm-en.py --run --models groq:openai/gpt-oss-120b --reference td1/reference-td1.csv --state state-new.jsonl --out traces-new.csv
```

avec `GROQ_API_KEY` / `OPENROUTER_API_KEY` définies dans le terminal, jamais dans un fichier du dépôt.

## Points ouverts

- Noms des membres pour les rôles B, F, G, H ; opérateur de `FULL-1` et de `A-op2-1`.
- Le groupe a fait bien plus d'appels que les 100 cellules du lot de base (319 tentatives : 239 Groq,
  80 OpenRouter). Les répétitions ne figuraient pas dans la répartition prévue. Elles sont conservées et
  étiquetées, jamais mêlées aux taux du lot de base.
