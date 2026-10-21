# THA validation

## Count sheet layout and protection: 19.0.1.0.5 (2026-10-21)

- Moved Lot / Serial, Stock Package, and Owner after the loose and packaging
  count fields. Updated upload parsing to validate the new visible layout.
- Enabled protected-sheet row and column formatting. Only yellow count cells
  remain editable; columns may be resized/hidden/unhidden, including the
  intentionally hidden technical ID columns.
- Python syntax and Git whitespace checks passed. THA module upgrade completed
  successfully, and Odoo was restarted. The test suite was not run.

Date: 2026-10-13. Version: 19.0.1.0.2.

## Installation and runtime

- Installed separately in Docker Odoo 19 database `THA`.
- Upgraded with:

  ```text
  docker exec odoo_19 odoo -d THA -u tha_stock_packaging_inventory_import --test-enable --test-tags /tha_stock_packaging_inventory_import --stop-after-init --http-port=8079 --max-cron-threads=0
  ```

- Command exited successfully. Odoo restarted afterward.
- Project `logs/server.log` reports `0 failed, 0 error(s) of 17 tests` at
  2026-10-13 06:29:31 UTC. The suite took 50.39 seconds, including fixture setup
  for 950 products.
- Verified installed module state and version through read-only database query.
- Authenticated HTTP verification confirmed both buttons in the combined
  Physical Inventory view. The download action returned HTTP 200 and a readable
  workbook for existing THA quant 330 (Coke, YGN/Stock/Ahlone).
- Workbook shows inventory unit ml, Bot (250 ml), Box (1250 ml), unlocked yellow
  count cells, locked labels, hidden identifiers and very-hidden template token.
  No conversion formulas or macros. Count and instruction sheets rendered and
  visually inspected. Download left this quant's counts and on-hand quantity
  unchanged.

## Coverage

- Mixed counts: Coke 100 + 3 x 250 + 2 x 1250 = 3350 ml;
  Sprite 0 + 1 x 250 + 2 x 1000 = 2250 ml.
- Preview does not update counts. Confirmation replaces exact existing counts.
- No extra quants, stock moves, accounting moves or changes to on-hand quantity.
- Zero counts, all-blank rows, invalid numbers, negative numbers, formulas,
  booleans, overflow and counts in disabled packaging slots.
- Altered labels, hidden IDs, headers and repeated stock-line IDs.
- Deleted quant IDs, changed locations, inventory precision and company scope.
- Removed packaging and changed conversion factors, including ancestor units,
  validated at upload and immediately before confirmation.
- Fresh export reflects changed packaging and newly added inventory lines.
- Separate lots, locations, stock packages and owners; lot/serial restrictions.
- Sum before rounding, fractional counts and packaging label rename.
- Concurrent count changes after preview block every update in the batch.
- Audit immutability, administrator permission checks, repeat-confirm protection,
  upload wizard and download actions.
- 950 products with different packaging sets exported, parsed, previewed and
  confirmed in rollback-managed test transactions. Existing quant count and
  on-hand quantities stayed unchanged.

## Remaining verification

- Native Microsoft Excel 2016 open/edit/save interaction was not performed.
  Standard XLSX protection and numeric validation were inspected programmatically;
  there are no modern Excel function dependencies.
- Browser rendering of the Odoo screens was not exercised. View installation,
  combined view buttons, HTTP download and wizard/model actions were verified.
- Production installation has not been performed. THA test records roll back;
  this validation did not submit physical counts on ordinary existing stock lines.
- Existing unrelated addon manifest warnings remain in the project log. Expected
  rejection tests also emit translation-source warnings from common helper
  functions; these are not test errors.

## Upload button RPC correction: 19.0.1.0.3

- Removed `@api.model` from the upload list-button method. Odoo's button RPC
  passes selected record IDs, which must be consumed as the method's recordset.
  The decorator previously made those IDs an unexpected positional argument.
- Added regression checks using Odoo `call_kw` with both an empty selection and
  selected inventory lines, beyond the original direct method test.
- Python/XML syntax and manifest data paths checked successfully.
- Upgraded THA and reran all 17 tests: zero failures/errors, 51.80 seconds.
  Project log confirmation: 2026-10-13 06:47:46 UTC.
- Restarted Odoo and verified authenticated HTTP calls to the actual
  `/web/dataset/call_button` endpoint with `args=[[]]` and `args=[[330]]`.
  Both returned the upload wizard action successfully. Its form view loaded
  with Preview Counts. No inventory values were written during HTTP verification.
- The first HTTP attempt arrived during restart and returned
  `RemoteDisconnected`; retry after startup succeeded.

## Product details in packaging errors: 19.0.1.0.4 (2026-10-15)

- Reference-unit validation now includes product display name/internal reference,
  packaging and inventory unit during download, upload and confirmation.
- Download collects every invalid product/packaging pair, deduplicating products
  repeated across inventory lines, and rejects before creating a template.
- Python/XML syntax, manifest data paths and Git whitespace checks passed.
- THA upgrade and all 19 module tests passed: zero failures/errors in 26.24s
  (project log: 2026-10-15 04:20:19 UTC). New tests cover multiple affected
  products, duplicate inventory lines, upload/confirmation details and no count
  writes on rejection.
- The first run had one test failure because archived packaging is filtered out
  by the existing membership check. The corrected regression uses mismatched
  reference units to exercise the requested conversion error.
- Restarted Odoo. Browser dialog rendering was not visually verified.
