# Prompts, exactly as used

Single version, used for every model and every run of TD 1 (21 October 2026). **Unchanged in TD 2**: TD 2
made no model call, and [`td2/check_prompts.py`](td2/check_prompts.py) rebuilds the twenty prompts from
`skeleton-multi-llm-en.py` and finds the same SHA-256 as all 319 rows of `traces-td1.csv`
([output](td2/check-prompts.txt)). Source: `SYSTEM_PROMPT` and `USER_PROMPT_TEMPLATE` in
[`skeleton-multi-llm-en.py`](skeleton-multi-llm-en.py); `{schema}` is [`schema.sql`](schema.sql),
`{question}` is the `question` of [`questions-td1.json`](questions-td1.json). Fingerprint:
`sha256(system + "\n" + user)`, stored in `prompt_sha256`.

## System message

```text
You write SQLite queries for a small e-commerce database. Reply with exactly one SQLite SELECT statement and nothing else: no explanation, no comments, no markdown other than an optional ```sql fence.
```

## User template

```text
Schema (SQLite):
{schema}

Conventions (binding):
- product.price is the unit price in euro cents, excluding VAT (an integer). Revenue excluding VAT is SUM(quantity_product * price), an integer number of cents.
- orders holds order lines: one row per (order_id, product_id). All lines of an order share the same customer_id and the same date.
- orders.date and customers.insert_date are UTC timestamps stored as text 'YYYY-MM-DD HH:MM:SS'. customers.birth_date is a date stored as text 'YYYY-MM-DD'. Compare them as text or with SQLite date functions.
- A period "from S to E" is closed on the left and open on the right: date >= S AND date < E.
- A customer's age on a day D is the number of completed years: someone born on B is N years old on D when the N-th anniversary of B is on or before D and the (N+1)-th anniversary is after D. "Exactly 25 years old" means completed age 25 on that day, computed from month and day, never from the year difference alone.
- Unless the question says "at the time of the order", ages are computed on the reference date given in the question.
- The query must return exactly one row and one column named revenue_cents. When no order line matches, return 0 (use COALESCE), not NULL.
- Use only the tables above. One SELECT statement, nothing else.

Question: {question}
```

## Variants

None. Kit parameters: temperature 0, output cap of the skeleton; no prompt variant was tried.
