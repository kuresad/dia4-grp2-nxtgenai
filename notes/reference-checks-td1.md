# TD 1 - How the references were computed and checked

`reference-td1.csv` holds, for C01 to C20, the SQL query written by the sub-group in step 1 (morning of
21 October 2026) and the integer value it returns on `data/boutique.sqlite`. No value comes from a model.
The file is kept exactly as produced in step 1; nothing in it was changed afterwards.

## Conventions applied (protocol, section 1)

| Convention | How the reference queries apply it |
|---|---|
| Period "from S to E", closed on the left, open on the right | `o.date >= 'S' AND o.date < 'E'` on the text timestamps (C01, C03-C07, C13-C15, C17-C20) |
| Completed age 25 on a reference date D | `c.birth_date > DATE(D, '-26 years') AND c.birth_date <= DATE(D, '-25 years')`: the 25th anniversary is on or before D and the 26th is after D; month and day count, never the year difference alone (C02, C08, C09, C11, C15-C17, C19) |
| Age 25 "at the time of the order" | the same interval computed from each order line's own date: `DATE(o.date, '-26 years')` and `DATE(o.date, '-25 years')` (C10, C18) |
| Product list | `o.product_id IN ('a', 'b', 'c')`, `IN ('a', 'c')` or `= 'd'` as written in the question (C03, C12-C14, C16, C17, C19) |
| Amount | `SUM(o.quantity_product * p.price)` in euro cents excluding VAT, joined on `product_id` |
| Nothing matches | `IFNULL(SUM(...), 0)` returns 0, not NULL (C06 and C14 are 0) |

## Independent check

Two checks were run on 21 October 2026 with `python scripts/verify_references.py`:

1. **The SQL of each row is re-executed** on the base opened read-only: one row, one column named
   `revenue_cents`, value equal to the CSV value.
2. **An independent recomputation in plain Python**, without SQL, from `data/product.csv`,
   `data/customers.csv` and `data/orders.csv`: completed age computed with
   `year difference - (birthday not yet reached)`, periods compared as text, products filtered as listed.

Result: the three values (CSV, SQL, Python) are equal for the 20 questions (`ALL OK`).

The base contains boundary customers that make the age convention observable: C001 is born on
2001-09-25 (25 exactly on 2026-09-25), C002 on 2001-09-24, C003 on 2001-09-26 and C004 on 2000-09-25
(26 on 2026-09-25). C02, C08 and C09 differ only by one day of reference date and give three different
values (590320, 605580, 487980): this is the expected effect of the anniversary boundary.

## Who wrote and who cross-checked each query

| Question | Written by | Cross-checked by |
|---|---|---|
| C01 | [TO COMPLETE] | [TO COMPLETE] |
| C02 | [TO COMPLETE] | [TO COMPLETE] |
| C03 | [TO COMPLETE] | [TO COMPLETE] |
| C04 | [TO COMPLETE] | [TO COMPLETE] |
| C05 | [TO COMPLETE] | [TO COMPLETE] |
| C06 | [TO COMPLETE] | [TO COMPLETE] |
| C07 | [TO COMPLETE] | [TO COMPLETE] |
| C08 | [TO COMPLETE] | [TO COMPLETE] |
| C09 | [TO COMPLETE] | [TO COMPLETE] |
| C10 | [TO COMPLETE] | [TO COMPLETE] |
| C11 | [TO COMPLETE] | [TO COMPLETE] |
| C12 | [TO COMPLETE] | [TO COMPLETE] |
| C13 | [TO COMPLETE] | [TO COMPLETE] |
| C14 | [TO COMPLETE] | [TO COMPLETE] |
| C15 | [TO COMPLETE] | [TO COMPLETE] |
| C16 | [TO COMPLETE] | [TO COMPLETE] |
| C17 | [TO COMPLETE] | [TO COMPLETE] |
| C18 | [TO COMPLETE] | [TO COMPLETE] |
| C19 | [TO COMPLETE] | [TO COMPLETE] |
| C20 | [TO COMPLETE] | [TO COMPLETE] |

Instructor check of the twenty values in session: [TO COMPLETE: values flagged as different, if any, and the correction made].
