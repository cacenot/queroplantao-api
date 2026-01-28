#!/usr/bin/env node

/**
 * Rewrite relative import/export specifiers to include explicit .js extensions
 * for Node.js ESM (NodeNext) compatibility.
 */

import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const SRC_DIR = path.join(__dirname, "..", "src");

const EXTENSIONLESS_SKIP = new Set([".js", ".mjs", ".cjs", ".json", ".node"]);

function isRelative(specifier) {
    return specifier.startsWith("./") || specifier.startsWith("../");
}

function hasKnownExtension(specifier) {
    const ext = path.extname(specifier);
    return EXTENSIONLESS_SKIP.has(ext);
}

function resolveSpecifier(specifier, fileDir) {
    if (!isRelative(specifier) || hasKnownExtension(specifier)) {
        return specifier;
    }

    const resolved = path.resolve(fileDir, specifier);

    if (fs.existsSync(`${resolved}.ts`) || fs.existsSync(`${resolved}.tsx`)) {
        return `${specifier}.js`;
    }

    if (
        fs.existsSync(resolved) &&
        fs.statSync(resolved).isDirectory() &&
        (fs.existsSync(path.join(resolved, "index.ts")) || fs.existsSync(path.join(resolved, "index.tsx")))
    ) {
        return `${specifier.replace(/\/$/, "")}/index.js`;
    }

    return specifier;
}

function rewriteImports(content, fileDir) {
    let updated = content;

    updated = updated.replace(/(\bfrom\s+["'])([^"']+)(["'])/g, (match, prefix, spec, suffix) => {
        const next = resolveSpecifier(spec, fileDir);
        return `${prefix}${next}${suffix}`;
    });

    updated = updated.replace(/(\bimport\s+["'])([^"']+)(["'])/g, (match, prefix, spec, suffix) => {
        const next = resolveSpecifier(spec, fileDir);
        return `${prefix}${next}${suffix}`;
    });

    return updated;
}

function processFile(filePath) {
    const content = fs.readFileSync(filePath, "utf-8");
    const updated = rewriteImports(content, path.dirname(filePath));

    if (content !== updated) {
        fs.writeFileSync(filePath, updated, "utf-8");
        console.log(`✓ Fixed imports: ${path.relative(SRC_DIR, filePath)}`);
    }
}

function walk(dirPath) {
    const entries = fs.readdirSync(dirPath);

    for (const entry of entries) {
        const entryPath = path.join(dirPath, entry);
        const stat = fs.statSync(entryPath);

        if (stat.isDirectory()) {
            walk(entryPath);
        } else if (entry.endsWith(".ts") && !entry.endsWith(".d.ts")) {
            processFile(entryPath);
        }
    }
}

console.log("🔧 Fixing ESM import specifiers in src...");

if (!fs.existsSync(SRC_DIR)) {
    console.error(`❌ Source directory not found: ${SRC_DIR}`);
    process.exit(1);
}

walk(SRC_DIR);

console.log("✅ ESM import fixes complete.");
