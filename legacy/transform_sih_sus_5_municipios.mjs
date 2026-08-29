import fs from "node:fs";
import path from "node:path";

const inputPath = process.argv[2];
const outputPath = process.argv[3];

if (!inputPath || !outputPath) {
  throw new Error("Usage: node transform_sih_sus.mjs <input.csv> <output.csv>");
}

const selectedCodes = new Set(["355030", "351880", "353440", "354780", "354870"]);
const monthMap = new Map([
  ["Jan", "01"], ["Fev", "02"], ["Mar", "03"], ["Abr", "04"],
  ["Mai", "05"], ["Jun", "06"], ["Jul", "07"], ["Ago", "08"],
  ["Set", "09"], ["Out", "10"], ["Nov", "11"], ["Dez", "12"],
]);

function parseDelimitedLine(line) {
  const fields = [];
  let value = "";
  let quoted = false;
  for (let i = 0; i < line.length; i += 1) {
    const char = line[i];
    if (char === '"') quoted = !quoted;
    else if (char === ";" && !quoted) {
      fields.push(value);
      value = "";
    } else value += char;
  }
  fields.push(value);
  return fields;
}

const text = fs.readFileSync(inputPath).toString("latin1");
const lines = text.split(/\r?\n/);
const headerIndex = lines.findIndex((line) => line.startsWith('"Município"'));
if (headerIndex < 0) throw new Error("DATASUS table header not found.");

const headers = parseDelimitedLine(lines[headerIndex]);
const outputRows = [[
  "municipio_codigo",
  "municipio_nome",
  "ano_mes_processamento",
  "internacoes",
  "uf",
  "fonte",
]];

const annualChecks = new Map();
for (const line of lines.slice(headerIndex + 1)) {
  const fields = parseDelimitedLine(line);
  if (fields.length !== headers.length || fields[0] === "Total") break;
  const match = fields[0].match(/^(\d{6})\s+(.+)$/);
  if (!match || !selectedCodes.has(match[1])) continue;

  const [, code, name] = match;
  let calculatedTotal = 0;
  for (let column = 1; column <= 12; column += 1) {
    const [, abbreviation] = headers[column].split("/");
    const value = fields[column] === "-" || fields[column] === "" ? 0 : Number(fields[column]);
    calculatedTotal += value;
    outputRows.push([
      code,
      name,
      `2025-${monthMap.get(abbreviation)}`,
      String(value),
      "SP",
      "DATASUS SIH/SUS - local de internação",
    ]);
  }
  annualChecks.set(code, { calculatedTotal, publishedTotal: Number(fields[13]) });
}

if (annualChecks.size !== selectedCodes.size) {
  throw new Error(`Expected ${selectedCodes.size} municipalities; found ${annualChecks.size}.`);
}
for (const [code, check] of annualChecks) {
  if (check.calculatedTotal !== check.publishedTotal) {
    throw new Error(`Annual total mismatch for municipality ${code}.`);
  }
}

fs.mkdirSync(path.dirname(outputPath), { recursive: true });
const csv = outputRows.map((row) => row.map((value) => `"${value.replaceAll('"', '""')}"`).join(";")).join("\n") + "\n";
fs.writeFileSync(outputPath, csv, "utf8");

console.log(JSON.stringify({
  outputPath,
  municipalities: annualChecks.size,
  rows: outputRows.length - 1,
  annualChecks: Object.fromEntries(annualChecks),
}, null, 2));
