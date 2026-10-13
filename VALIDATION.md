# THA validation

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
