# IA générative de confiance : sous-groupe DIA4 GRP2

ESILV, Next-Generation AI (MESIIN475926), Didier Parisot. Dépôt public du sous-groupe pour les TD 1, 2 et 3.

| Élément | Valeur |
|---|---|
| Sous-groupe | GRP2 |
| Membres | Jason ZOH, Kuresa RAMEN, Paul CHARMOILLE, Enzo SIERRA-GUISSET, Roy WEHBE, Yohan ALLOUCHE, Florent SEYDOUX, Thomas ANQUETIN |
| Version du pack | `2026-10-14-students-1` (kit du 14 octobre 2026) |
| Base de données | `data/boutique.sqlite`, SHA-256 `0077e235adc2ca647b484e3083c98a6d7cae3ef3655ce366a299caf13398fec2`, graine 20260925, identique à `data/manifest.json` |
| Environnement | Windows 11, Python 3.14.7, SQLite 3.50.4, `requests` dans un `.venv` (seulement pour `check_access.py`) ; le skeleton et les scripts n'utilisent que la bibliothèque standard |
| Dépôt | <https://github.com/kuresad/dia4-grp2-nxtgenai> |

## Organisation

```text
.
├── README.md                  ce fichier
├── reports/                   un rapport de séance par TD (td1.md, td2.md, td3.md)
├── td1/                       livrables du TD 1 : références, traces, comparaison, synthèse, prompts
├── td2/                       livrables du TD 2 : vote (A-quorum), faux consensus (B-consensus),
│                              routage (C-routing), revues croisées (reviews), module commun (common.py)
├── td3/                       TD 3 (à venir)
│
│   Kit, commun aux trois TD (laissé à la racine : chaque script cherche ses ressources à côté de lui)
├── skeleton-multi-llm-en.py   orchestrateur multi-modèles ; vote_k_sur_n complété au TD 2
├── atelier-vote.py            atelier de vote du TD 2 (kit, non modifié)
├── atelier-routage.py         simulateur de routage des TD 2 et 3 (kit, non modifié)
├── sandbox_sqlite.py          bac à sable SQL en lecture seule
├── check_access.py            vérification d'accès aux cinq modèles
├── verify-data.py             empreintes de la base et des CSV
├── data/                      boutique.sqlite, ses CSV et son manifeste
├── schema.sql, questions-td1.json, modeles-autorises.json
└── .gitignore, .gitattributes clés, environnements et caches exclus ; données du kit gardées identiques à l'octet
```

## État par séance

| TD | Date | Dossier | Rapport | Résumé |
|---|---|---|---|---|
| TD 1 | 21 octobre 2026 | [`td1/`](td1/README.md) | `reports/td1.md` (**manquant**) | 20 références ; 319 tentatives sur 11 runs de 5 modèles ; lot de base : gpt-oss-20b 20/20, gpt-oss-120b 18/20, qwen3.8-27b 16/20, dots-3-note 14/20, north-mini-code 10/20 |
| TD 2 | 18 novembre 2026 | [`td2/`](td2/README.md) | [`reports/td2.md`](reports/td2.md) | `vote_k_sur_n` (19/19 tests) ; panel fixe 2 sur 3 sur le lot de base : 16 consensus, 0 faux, 4 abstentions, mais faux consensus sur C09 avec d'autres runs ; faux consensus expliqués ; règle de routage et simulateur avant et après ; [six revues croisées](td2/reviews/README.md) |
| TD 3 | à venir | `td3/` | `reports/td3.md` | feuille de coûts, cas d'usage, diapositives, démonstration |

## Vérification rapide (sans réseau, depuis la racine)

```bash
python verify-data.py                                   # "ok": true
python check_access.py --no-network                     # Python, empreintes de la base et des CSV
python skeleton-multi-llm-en.py --rates --state td1/traces-td1-base.jsonl --reference td1/reference-td1.csv
python td2/A-quorum/test_vote.py                        # 19/19 tests
python td2/C-routing/atelier-routage-grp2.py            # notre règle de routage sur les scénarios
```

Toutes les commandes du TD 1 et du TD 2 sont dans [`td1/README.md`](td1/README.md) et
[`td2/README.md`](td2/README.md). Un nouvel appel aux modèles demande `GROQ_API_KEY` / `OPENROUTER_API_KEY`
dans le terminal, jamais dans un fichier du dépôt.

## Hygiène du dépôt

Aucune clé, aucun `.env`, aucune capture de compte n'est commitée. Le `.gitignore` du kit est à la racine
(fichiers d'environnement, clés, `.venv/`, caches, `ready-for-td1.txt`). La sortie de `check_access.py` du
18 octobre 2026 (les cinq modèles OK) reste sur les machines des membres, comme le prévoit le `.gitignore`.

## Assistance IA

L'assistance IA est déclarée, avec les prompts tels qu'ils ont été utilisés :
[`td2/ai-assistance-en.md`](td2/ai-assistance-en.md).

## Points ouverts

- `reports/td1.md` reste à écrire.
- Les contributions de chaque membre au TD 2, dans [`reports/td2.md`](reports/td2.md).
- TD 1 : rôles B, F, G, H, opérateur de `FULL-1` et de `A-op2-1` ([`td1/README.md`](td1/README.md)).
