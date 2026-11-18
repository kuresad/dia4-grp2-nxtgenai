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
