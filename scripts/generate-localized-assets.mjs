#!/usr/bin/env node

import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const catalogPath = resolve(root, "assets/localization.json");
const mascotPath = resolve(root, "assets/mascot/base/mascot_base_front_v1_512.png");
const locales = ["en", "ko", "ja", "zh"];
const cardIds = ["scan_first", "backup_first", "api_notice", "unsupported"];
const mode = process.argv[2] ?? "--write";

if (mode !== "--write" && mode !== "--check") {
  console.error("Usage: node scripts/generate-localized-assets.mjs [--write|--check]");
  process.exit(2);
}

function escapeXml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&apos;");
}

function assertCatalog(catalog) {
  if (catalog.version !== 1 || !catalog.locales) {
    throw new Error("Unsupported localization catalog format.");
  }
  const actualLocales = Object.keys(catalog.locales).sort().join(",");
  if (actualLocales !== [...locales].sort().join(",")) {
    throw new Error("Expected exactly the en, ko, ja, and zh locales.");
  }

  for (const locale of locales) {
    const entry = catalog.locales[locale];
    if (!entry.name || !entry.social?.description || !entry.social?.descriptor?.length || !entry.social?.tagline?.length) {
      throw new Error("Incomplete social copy for locale: " + locale);
    }
    for (const cardId of cardIds) {
      const card = entry.cards?.[cardId];
      if (!card?.title || !card?.description || !card?.body?.length || card.body.some((paragraph) => !paragraph.length)) {
        throw new Error("Incomplete " + cardId + " copy for locale: " + locale);
      }
    }
  }
}

function svgStart(locale, width, height, title, description) {
  return [
    '<svg xmlns="http://www.w3.org/2000/svg" ',
    'width="', width, '" height="', height, '" viewBox="0 0 ', width, " ", height, '" ',
    'role="img" aria-labelledby="svg-title svg-desc" lang="', locale, '" xml:lang="', locale, '">',
    "<title id=\"svg-title\">", escapeXml(title), "</title>",
    "<desc id=\"svg-desc\">", escapeXml(description), "</desc>"
  ].join("");
}

function fontStyles() {
  return [
    "<style>",
    ".brand { font-family: 'Avenir Next', Nunito, 'Apple SD Gothic Neo', 'Noto Sans CJK KR', 'Noto Sans CJK JP', 'PingFang SC', 'Microsoft YaHei UI', sans-serif; font-weight: 800; }",
    ".copy { font-family: 'Avenir Next', Nunito, 'Apple SD Gothic Neo', 'Noto Sans CJK KR', 'Noto Sans CJK JP', 'PingFang SC', 'Microsoft YaHei UI', sans-serif; }",
    "</style>"
  ].join("");
}

function renderSocial(locale, copy, mascotData, documentOnlyNote) {
  const title = "PomiTranslate — World Translator for Minecraft";
  const descriptor = copy.descriptor.map(escapeXml).join(" ");
  const tagline = copy.tagline.map(escapeXml).join(" ");
  const description = copy.description + " " + descriptor + " " + tagline;
  const imageData = "data:image/png;base64," + mascotData;
  const descriptorLines = copy.descriptor.map((line, index) =>
    '<tspan x="72" y="' + (354 + index * 40) + '">' + escapeXml(line) + "</tspan>"
  ).join("");
  const taglineLines = copy.tagline.map((line, index) =>
    '<tspan x="74" y="' + (462 + index * 34) + '">' + escapeXml(line) + "</tspan>"
  ).join("");
  const noteLine = documentOnlyNote
    ? '<text x="76" y="555" class="copy" fill="#5C564F" font-size="18" font-weight="500">' + escapeXml(documentOnlyNote) + "</text>"
    : "";

  return [
    svgStart(locale, 1200, 630, title, description),
    "<defs>",
    '<linearGradient id="background" x1="0" y1="0" x2="1" y2="1">',
    '<stop offset="0" stop-color="#FBF7F0"/>',
    '<stop offset="1" stop-color="#EAF2FF"/>',
    "</linearGradient>",
    "</defs>",
    '<rect width="1200" height="630" fill="url(#background)"/>',
    '<circle cx="954" cy="314" r="250" fill="#DCEAFF" opacity="0.78"/>',
    fontStyles(),
    '<text x="72" y="252" class="brand" font-size="58" letter-spacing="-1.1">',
    '<tspan fill="#3A342E">Pomi</tspan><tspan fill="#2F6FED">Translate</tspan>',
    "</text>",
    '<text x="76" y="294" class="copy" fill="#3A342E" font-size="24" font-weight="650">',
    "World Translator for Minecraft</text>",
    '<text class="copy" fill="#3A342E" font-size="32" font-weight="650">',
    descriptorLines,
    "</text>",
    '<text class="copy" fill="#0B756C" font-size="23" font-weight="700">',
    taglineLines,
    "</text>",
    noteLine,
    '<image x="710" y="72" width="488" height="488" preserveAspectRatio="xMidYMid meet" ',
    'href="', imageData, '"/>',
    "</svg>",
    "\n"
  ].join("");
}

function renderGuide(locale, cardId, copy, mascotData) {
  const title = copy.title + " — PomiTranslate";
  const description = copy.description;
  const imageData = "data:image/png;base64," + mascotData;
  let y = 282;
  const body = copy.body.map((paragraph, paragraphIndex) => {
    const lines = paragraph.map((line) => {
      const tspan = '<tspan x="84" y="' + y + '">' + escapeXml(line) + "</tspan>";
      y += 39;
      return tspan;
    }).join("");
    if (paragraphIndex < copy.body.length - 1) y += 24;
    return lines;
  }).join("");

  return [
    svgStart(locale, 1200, 720, title, description),
    "<defs>",
    '<linearGradient id="background" x1="0" y1="0" x2="1" y2="1">',
    '<stop offset="0" stop-color="#FBF7F0"/>',
    '<stop offset="1" stop-color="#EAF2FF"/>',
    "</linearGradient>",
    "</defs>",
    '<rect width="1200" height="720" fill="url(#background)"/>',
    '<rect x="40" y="40" width="1120" height="640" rx="36" fill="#FFFEFC"/>',
    '<circle cx="944" cy="360" r="232" fill="#E5EEFF"/>',
    '<rect x="84" y="104" width="58" height="7" rx="3.5" fill="#0B756C"/>',
    fontStyles(),
    '<text x="84" y="198" class="copy" fill="#3A342E" font-size="44" font-weight="780">',
    escapeXml(copy.title),
    "</text>",
    '<text class="copy" fill="#3A342E" font-size="27" font-weight="500" letter-spacing="0.05">',
    body,
    "</text>",
    '<image x="710" y="124" width="468" height="468" preserveAspectRatio="xMidYMid meet" ',
    'href="', imageData, '"/>',
    "</svg>",
    "\n"
  ].join("");
}

const catalog = JSON.parse(readFileSync(catalogPath, "utf8"));
assertCatalog(catalog);
const mascotBuffer = readFileSync(mascotPath);
const pngSignature = Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]);
if (!mascotBuffer.subarray(0, 8).equals(pngSignature)) {
  throw new Error("Mascot source is not a PNG: " + mascotPath);
}
const mascotData = mascotBuffer.toString("base64");
const outputs = [];

for (const locale of locales) {
  const entry = catalog.locales[locale];
  outputs.push([
    resolve(root, "assets/brand/social/og_default_" + locale + "_v1.svg"),
    renderSocial(locale, entry.social, mascotData, entry.documentOnlyNote)
  ]);
  for (const cardId of cardIds) {
    outputs.push([
      resolve(root, "assets/illustrations/docs/doc_" + cardId + "_" + locale + "_v1.svg"),
      renderGuide(locale, cardId, entry.cards[cardId], mascotData)
    ]);
  }
}

const differences = [];
for (const [path, content] of outputs) {
  let current = null;
  try {
    current = readFileSync(path, "utf8");
  } catch (error) {
    if (error.code !== "ENOENT") throw error;
  }
  if (current === content) continue;
  differences.push(path);
  if (mode === "--write") {
    mkdirSync(dirname(path), { recursive: true });
    writeFileSync(path, content, "utf8");
  }
}

if (mode === "--check") {
  if (differences.length) {
    console.error("Localized SVGs are missing or out of date:");
    for (const path of differences) console.error("  " + path.replace(root + "/", ""));
    process.exit(1);
  }
  console.log("Localized SVGs are current (" + outputs.length + " files).");
} else {
  console.log("Generated " + differences.length + " localized SVG file(s).");
}
