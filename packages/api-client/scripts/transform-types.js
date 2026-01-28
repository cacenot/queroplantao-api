#!/usr/bin/env node

/**
 * Post-processing script to transform generated TypeScript types from snake_case to camelCase.
 *
 * This script runs after Orval generates types and transforms all property names
 * in type definitions to match the runtime camelCase transformation done by humps.
 */

import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const MODELS_DIR = path.join(__dirname, "..", "src", "client", "models");

/**
 * Convert snake_case to camelCase
 */
function toCamelCase(str) {
    return str.replace(/_([a-z])/g, (_, letter) => letter.toUpperCase());
}

/**
 * Transform property names in a TypeScript type definition
 */
function transformTypeDefinition(content) {
    // Match property definitions like: property_name: Type or property_name?: Type
    return content.replace(/(\s+)([a-z_]+)(\??:)/g, (match, spaces, propName, optional) => {
        // Skip if already camelCase or if it's a type name
        if (!propName.includes("_")) {
            return match;
        }

        const camelName = toCamelCase(propName);
        return `${spaces}${camelName}${optional}`;
    });
}

/**
 * Process a single TypeScript file
 */
function processFile(filePath) {
    const content = fs.readFileSync(filePath, "utf-8");
    const transformed = transformTypeDefinition(content);

    if (content !== transformed) {
        fs.writeFileSync(filePath, transformed, "utf-8");
        console.log(`✓ Transformed: ${path.basename(filePath)}`);
    }
}

/**
 * Process all TypeScript files in a directory
 */
function processDirectory(dirPath) {
    const files = fs.readdirSync(dirPath);

    for (const file of files) {
        const filePath = path.join(dirPath, file);
        const stat = fs.statSync(filePath);

        if (stat.isDirectory()) {
            processDirectory(filePath);
        } else if (file.endsWith(".ts")) {
            processFile(filePath);
        }
    }
}

// Main execution
console.log("🔄 Transforming generated types to camelCase...\n");

if (!fs.existsSync(MODELS_DIR)) {
    console.error(`❌ Models directory not found: ${MODELS_DIR}`);
    process.exit(1);
}

processDirectory(MODELS_DIR);

console.log("\n✅ Type transformation complete!");
