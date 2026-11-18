# AI assistance used for TD 2

The submission guide asks for the prompts used for coding help to be kept as they were used.

- **Tool**: Claude Code (Anthropic, model Claude Opus 5.5) in VS Code, on Roy WEHBE's machine, 18 November 2026.
- **Scope**: the code in `td2/` (`A-quorum/`, `B-consensus/`, `C-routing/`, `check_prompts.py`), the
  `vote_k_sur_n` method of `skeleton-multi-llm-en.py`, the Markdown write-ups and `reports/td2.md`.
- **No model of the experiment was called**: every figure comes from the stored TD 1 traces, replayed
  offline. The assistant read the TD 2 statement, the lecture CM2 and the repository, ran the scripts and
  wrote the files. The group checks the results against the evidence files listed in `reports/td2.md`.

## Prompt, as used (French, verbatim)

> Tu vas maintenant effectuer le TD2 Intégralement, en prenant en compte les trois différentes parties
> figurant dans les consignes. L'entièreté des consignes pour ce cours figurent sur ce lien :
> https://storage.googleapis.com/docs.g.quanticfactory.io/ESILV/next-generation-ai/latest/students/kit-td1/enonce-td2-en.html
> Le lien du CM2 qu'il faudra prendre en compte figure également sur ce lien :
> https://storage.googleapis.com/docs.g.quanticfactory.io/ESILV/next-generation-ai/latest/students/lectures/cm2-en.html
> Je t'ai également mis l'architecture demandée pour le github de ce cours, qui est déjà connecté à ce
> dossier. A toi de modifier le repository pour pouvoir bien répondre à ces consignes.
> Effectue le TD en entier et reviens vers moi si tu as quelconque question. Je te laisse le contrôle total.

Steps 1 and 2 (`td2/A-quorum`, `td2/B-consensus`, the `vote_k_sur_n` method) were already present,
uncommitted, in the working copy when this session started (files dated 18 November, 14:41 to 14:44). This
session re-ran them and checked their outputs, then added the commentary, step 3 and the report. Who wrote
them, and with which prompt, is to be confirmed by the group.

## Later prompts of the same session (French, verbatim)

Repository layout:

> Avant que je pousse pour terminer organise le dossier github pour avoir la partie td1 dans son dossier et
> td2 dans son dossier (deja fait) et un readme generale aussi. aussi j'ai deja pousser vers github verifie.

Cross-reviews (`td2/reviews/`) and the fixes they cite:

> Apparement chaque groupe A[1] (Jason et Yohan), B[2] (Roy , Enzo, Florent) et C[3] (Kuresa, Paul et
> Thomas) doit faire un review de la partie des uns et autres, on doit expliquer les erreurs du groupe et
> expliquer les retry, c'est en d'autre terme une analyse du code des autres. Donc sert toi aussi des echecs
> que tu eu comme idée pour les analyses. le prof dit qu'on est censé dire si on aurai pu faire mieux, s'il ya
> un bug ou quelque chose de problematique la review doit indiquer les ameliorations faites pour ameliorer le
> code. Fais en sorte que les review n'adresse pas forcement le meme probleme ou ameliorations si une review
> l'a deja faite. Tu comprends ? explique ce que tu as compris avant que tu puisse commencer.

> 1. Six reviews. 2. b. s'il ya encore des ameliorations (ne prends pas en compte les erreurs que seul une ia
> peut faire) mais base toi aussi sur des modifications que tu as du faire qui ameliorait le code. 3. refais
> les readme et les reviews en francais. Tu peux faire un dossier reviews mais repeter dans chaque step
> (A-quorumetc...)

The groups read and checked the reviews before the hand-in; each fix is in its own commit, cited in the review.
