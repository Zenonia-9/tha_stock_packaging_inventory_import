# Physical Inventory Counts by Packaging

Odoo 19 addon for importing physical counts into **existing** stock quant lines.
It does not create quants, apply inventory adjustments, change on-hand quantity,
or post valuation entries.

## Workflow

1. Select the correct company. Open Inventory → Operations → Physical Inventory.
2. Save any newly added lines. Select the lines to count and click
   **Download Packaging Count Sheet**.
3. Enter numbers in the yellow count cells. Each line already shows its base
   unit and all active product packagings, ordered by conversion size.
   Gray slots are unused. Names and identities are protected against accidental
   editing. No formulas, dropdowns or macros are required. The standard `.xlsx`
   format is designed for Excel 2016; native Excel 2016 interaction has not been
   verified in this run.
4. Leave every count blank to skip a line. On a counted line, blank count cells
   mean zero. Enter an explicit zero to record zero stock.
5. Click **Upload Packaging Counts**, choose the file, and **Preview Counts**.
6. Review old/new counts and conversions. Click **Update Counted Quantities**.
7. Click **View Inventory Lines**. Apply using Odoo's normal **Apply** workflow.

Example: 100 ml + 3 bottles containing 250 ml + 2 boxes containing 1250 ml
replaces the existing counted quantity with 3350 ml. Re-uploading replaces the
absolute count; it never adds another 3350 ml.

## Refresh and validation

Download fresh templates when products or packagings change. Snapshots are saved
on the server and scoped to the current company/database. Hidden workbook IDs
are validated against that snapshot. Counted packaging membership and conversion
factors are rechecked on upload and confirmation. Unit precision changes, stale
stock identities and counts/stock changed after preview block confirmation.
New products first need their normal Physical Inventory lines before export.
Different lots, serials, locations, stock packages and owners retain separate rows.
Serial-number totals must be zero or one; tracked counts require an existing lot.

Counts must be finite nonnegative numbers. Text, formulas, duplicate stock-line
IDs, modified identifying labels, unexpected columns and unused-slot counts are
rejected. Blank rows/products are never reset to zero. Omitted rows remain untouched.

Inventory administrators can use these actions. Multi-company rules and normal
stock quant access rights apply. All rows validate before any write, and ORM row
locks protect confirmation. Template and import audit records are immutable to
ordinary RPC writes; successful batches cannot be confirmed twice.

Audit history: Inventory → Operations → Packaging Count Imports. Each batch keeps
the source file, entered packaging counts, conversion factors, previous count,
new count, responsible user and confirmation time.

## Dependencies and checks

- `stock`; Python `openpyxl` and `xlsxwriter`.
- Maximum 20,000 selected stock lines and 10 MB uploaded `.xlsx` files.
- Run Odoo tests with `--test-tags /tha_stock_packaging_inventory_import`.
- Tests run inside rollback-managed Odoo transactions; test records are not
  intended for normal inventory use.

See [VALIDATION.md](VALIDATION.md) for the THA installation and validation results.
