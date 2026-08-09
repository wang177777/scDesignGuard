import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const artifactModulePath = process.env.ARTIFACT_TOOL_MODULE;
if (!artifactModulePath) {
  throw new Error("Set ARTIFACT_TOOL_MODULE to the artifact_tool.mjs supplied by the document runtime.");
}
const { SpreadsheetFile, Workbook } = await import(artifactModulePath);
const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const root = process.env.SDG_WORKTREE ?? path.resolve(scriptDir, "../../../..");
const sourceDir = path.join(root, "reports/final_story_only_submission_20260809/source_sheets");
const outDir = path.join(root, "delivery/scDesignGuard_Nature_Methods_FINAL_SUBMISSION_PACKAGE_20260809");
const previewDir = path.join(root, "reports/final_story_only_submission_20260809/source_data_previews");
const outputPath = path.join(outDir, "scDesignGuard_Nature_Methods_SOURCE_DATA.xlsx");

const sheets = [
  ["README", "README.csv"],
  ["Fig1", "Fig1.csv"],
  ["Fig2_Benchmark", "Fig2_Benchmark.csv"],
  ["Fig2_Endpoints", "Fig2_Endpoints.csv"],
  ["Fig3_E2E", "Fig3_E2E.csv"],
  ["Fig4_Invalidities", "Fig4_Invalidities.csv"],
  ["Fig4_Transport", "Fig4_Transport.csv"],
  ["Fig4_Software", "Fig4_Software.csv"],
  ["Fig5_Composition", "Fig5_Composition.csv"],
  ["Fig5_Effects", "Fig5_Composition_Effects.csv"],
  ["Fig5_Expression", "Fig5_Expression.csv"],
  ["Fig5_Pathway", "Fig5_Pathway.csv"],
  ["Fig5_Atlas", "Fig5_Atlas.csv"],
  ["ED1_Support", "ED1_Support.csv"],
  ["ED1_LODO", "ED1_LODO.csv"],
  ["ED1_Calibration", "ED1_Calibration.csv"],
  ["ED2_Primary", "ED2_Primary.csv"],
  ["ED2_Secondary", "ED2_Secondary.csv"],
  ["ED2_Software", "ED2_Software.csv"],
  ["ED3_Challenges", "ED3_Challenges.csv"],
  ["ED3_Transport", "ED3_Transport.csv"],
  ["ED3_Matched", "ED3_Matched.csv"],
  ["ED4_LODO", "ED4_LODO.csv"],
  ["ED4_Direction", "ED4_Direction.csv"],
  ["ED4_Filter", "ED4_Filter.csv"],
  ["ED4_InvalidDE", "ED4_InvalidDE.csv"],
  ["ED4_NullPerm", "ED4_NullPerm.csv"],
  ["ED5_MDS", "ED5_MDS.csv"],
  ["ED5_Support", "ED5_Support.csv"],
  ["ED5_Composition", "ED5_Composition.csv"],
  ["ED6_DE", "ED6_DE.csv"],
  ["ED6_Pathways", "ED6_Pathways.csv"],
  ["ED6_Method", "ED6_Method.csv"],
  ["ED6_Atlas", "ED6_Atlas.csv"],
];

function formatSheet(sheet, isLarge = false, isReadme = false) {
  const used = sheet.getUsedRange();
  if (!isLarge) {
    used.format.font = { name: "Arial", size: 9, color: "#25313B" };
    used.format.borders = { preset: "all", style: "thin", color: "#D9E1E5" };
    used.format.verticalAlignment = "center";
    used.format.wrapText = false;
  }
  const header = used.getRow(0);
  header.format = {
    fill: "#1F4E79",
    font: { name: "Arial", size: 9, bold: true, color: "#FFFFFF" },
    wrapText: true,
    verticalAlignment: "center",
    horizontalAlignment: "center",
    borders: { preset: "all", style: "thin", color: "#FFFFFF" },
  };
  header.format.rowHeight = 32;
  sheet.freezePanes.freezeRows(1);
  sheet.showGridLines = false;
  if (isReadme) {
    used.format.wrapText = true;
    used.getColumn(0).format.columnWidth = 18;
    used.getColumn(1).format.columnWidth = 28;
    used.getColumn(2).format.columnWidth = 48;
    used.getColumn(3).format.columnWidth = 56;
    used.format.autofitRows();
  } else if (isLarge) {
    used.format.columnWidth = 16;
    used.getColumn(0).format.columnWidth = 20;
    used.getColumn(1).format.columnWidth = 20;
  } else {
    // A consistent, bounded width keeps long accessions, hashes and reason
    // strings readable without turning the workbook into a horizontal poster.
    used.format.columnWidth = 16;
    used.getColumn(0).format.columnWidth = 20;
    used.format.autofitRows();
    header.format.rowHeight = 32;
  }
}

await fs.mkdir(outDir, { recursive: true });
await fs.mkdir(previewDir, { recursive: true });

let workbook = null;
for (let i = 0; i < sheets.length; i += 1) {
  const [sheetName, fileName] = sheets[i];
  const csvText = await fs.readFile(path.join(sourceDir, fileName), "utf8");
  if (workbook === null) {
    workbook = await Workbook.fromCSV(csvText, { sheetName });
  } else {
    await workbook.fromCSV(csvText, { sheetName });
  }
  formatSheet(workbook.worksheets.getItem(sheetName), sheetName === "ED6_DE", sheetName === "README");
}

const inspected = await workbook.inspect({
  kind: "workbook,sheet",
  maxChars: 12000,
  tableMaxRows: 3,
  tableMaxCols: 8,
  tableMaxCellChars: 80,
});
await fs.writeFile(path.join(previewDir, "workbook_inspect.ndjson"), inspected.ndjson, "utf8");

// Export the complete workbook before allocating any render surfaces. This is
// important for ED6, which retains all 100,434 eligible gene-by-cluster tests.
const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(outputPath);
workbook = null;
if (globalThis.gc) globalThis.gc();

// Visual QA previews use each sheet's exact header and first 24 source rows.
// This keeps the preview surface bounded while the exported workbook preserves
// every row without truncation.
for (const [sheetName, fileName] of sheets) {
  const csvText = await fs.readFile(path.join(sourceDir, fileName), "utf8");
  const previewLines = csvText.split(/\r?\n/).slice(0, 25).join("\n") + "\n";
  const previewWb = await Workbook.fromCSV(previewLines, { sheetName });
  formatSheet(previewWb.worksheets.getItem(sheetName), false, sheetName === "README");
  const preview = await previewWb.render({ sheetName, autoCrop: "all", scale: 0.75, format: "png" });
  await fs.writeFile(path.join(previewDir, `${sheetName}.png`), new Uint8Array(await preview.arrayBuffer()));
}
console.log(JSON.stringify({ outputPath, sheetCount: sheets.length, sheets: sheets.map(([name]) => name) }, null, 2));
