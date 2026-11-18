# Revues croisées du TD 2

Chaque groupe a relu les deux étapes qu'il n'a pas écrites : six revues, deux par étape. Les deux revues
d'une même étape ne traitent **pas les mêmes problèmes** : chacune renvoie à l'autre en en-tête. Chaque
correction appliquée a son propre commit, cité dans la revue. Une copie des deux revues d'une étape se
trouve aussi dans le dossier de l'étape (`A-quorum/reviews/`, `B-consensus/reviews/`, `C-routing/reviews/`).
Le dossier présent fait référence ; les copies sont régénérées à partir de lui.

| Groupe | Membres | Auteur de |
|---|---|---|
| A [1] | Jason ZOH, Yohan ALLOUCHE | étape 1, quorum ([`A-quorum/`](../A-quorum/)) |
| B [2] | Roy WEHBE, Enzo SIERRA-GUISSET, Florent SEYDOUX | étape 2, faux consensus ([`B-consensus/`](../B-consensus/)) |
| C [3] | Kuresa RAMEN, Paul CHARMOILLE, Thomas ANQUETIN | étape 3, routage ([`C-routing/`](../C-routing/)) |

## Les six revues

| Revue | Relecteurs → étape | Problèmes traités | Commit des corrections |
|---|---|---|---|
| [revue-B-etape1.md](revue-B-etape1.md) | B → 1 | verdict inconnu ignoré en silence ; même famille comptée deux fois ; tests qui ne vérifient pas les modèles d'accord | [`0103770`](https://github.com/kuresad/dia4-grp2-nxtgenai/commit/01037707e8240f7a8859d8d5482ed46e1275b717) |
| [revue-C-etape1.md](revue-C-etape1.md) | C → 1 | fichier multi-runs → faux consensus silencieux (C09) ; statut « unavailable » trop vague, n codé en dur ; **analyse des retry** (429, quota OTPM de qwen) | [`0a4c083`](https://github.com/kuresad/dia4-grp2-nxtgenai/commit/0a4c0832ab44cae9e4875beecc8016d9a48ac4df) |
| [revue-A-etape2.md](revue-A-etape2.md) | A → 2 | cas choisis à la main : C09 manqué, le panel déclaré se trompe 12 fois sur 40 ; contrôle « non vide » affirmé et non mesuré | [`17d7258`](https://github.com/kuresad/dia4-grp2-nxtgenai/commit/17d7258ed9a1536cff2531127deef7fcccf85a24) |
| [revue-C-etape2.md](revue-C-etape2.md) | C → 2 | logique copiée dans 4 scripts (dont le `KeyError: 'value'`) ; le « 0 » imposé par le prompt (proposition pour le TD 3) | [`71bde99`](https://github.com/kuresad/dia4-grp2-nxtgenai/commit/71bde996368bbaa489624bc1577bf187871ef185) |
| [revue-A-etape3.md](revue-A-etape3.md) | A → 3 | capacités recopiées à la main ; éligibilité sur un seul run ; quorum qui compte un membre inéligible | [`2e3b593`](https://github.com/kuresad/dia4-grp2-nxtgenai/commit/2e3b593353e02c4375fc51838cdf25e100ac9c8a) |
| [revue-B-etape3.md](revue-B-etape3.md) | B → 3 | tokens et latences recopiés ; chemins codés en dur ; référence en 5 min et budget arbitraire (non corrigés, à trancher au TD 3) | [`25be186`](https://github.com/kuresad/dia4-grp2-nxtgenai/commit/25be186a5a40d819d1103d8a31e1dcb8b6aa757a) |

## Ce que les revues changent aux résultats

- **Tests du vote** : 16/16 → 19/19 (verdict inconnu, même famille, liste des modèles d'accord vérifiée).
- **Faux consensus** : la conclusion « le panel déclaré n'en produit aucun » était trop forte. Sur C09, il
  renvoie 0 dans 12 des 40 combinaisons d'un run par membre. Le lot de base y échappe parce que qwen y
  a eu juste dans ce run précis (cas WC-4).
- **Routage** : décisions inchangées avec le critère de l'énoncé. Avec le critère « tous les runs », la
  question d'âge destinée à un versement passe sur gpt-oss-120b avec une référence.
- **Retry** : les 429 du TD 1 étaient prévisibles. qwen produit environ 2 300 tokens de sortie par minute au
  rythme du skeleton, pour un quota de 1 000 ; il aurait fallu environ 8 s entre les requêtes au lieu de 3.

Les tables des 20 décisions du lot de base et de FULL-1 sont inchangées. La seule différence est le libellé
d'un membre sans voix (`sql_invalid` au lieu de `unavailable`).

## Méthode

- Chaque problème est appuyé sur une preuve qu'on peut relancer (commande, fichier de sortie, cellule de
  trace), et chaque correction a été vérifiée en régénérant toutes les sorties.
- Une correction qui ne doit rien changer (refactoring) a été vérifiée en comparant les sorties, octet par
  octet, avant et après.
- Ce qui n'a pas été corrigé est dit et justifié : prompt et pause du skeleton figés pendant le TD 2,
  décisions qui relèvent du TD 3.
