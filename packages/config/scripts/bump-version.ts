import { readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";

function bumpVersion(version: string): string {
  const parts = version.split(".").map(Number);
  if (parts.length !== 3 || parts.some(Number.isNaN)) {
    throw new Error(`Invalid version format: ${version}`);
  }
  const [major, minor, patch] = parts as [number, number, number];
  return `${major}.${minor}.${patch + 1}`;
}

function updatePythonVersion() {
  const pyprojectPath = join(__dirname, "../python/pyproject.toml");
  const content = readFileSync(pyprojectPath, "utf8");
  const versionMatch = content.match(/version = "(\d+\.\d+\.\d+)"/);

  if (!versionMatch?.[1]) {
    throw new Error("Could not find valid version in pyproject.toml");
  }

  const newVersion = bumpVersion(versionMatch[1]);
  const newContent = content.replace(
    /version = "(\d+\.\d+\.\d+)"/,
    `version = "${newVersion}"`,
  );
  writeFileSync(pyprojectPath, newContent);
  return newVersion;
}

function updateTypeScriptVersion() {
  const packagePath = join(__dirname, "../typescript/package.json");
  const pkg = JSON.parse(readFileSync(packagePath, "utf8")) as {
    version: string;
  };

  if (!pkg.version) {
    throw new Error("No version field found in package.json");
  }

  const newVersion = bumpVersion(pkg.version);
  pkg.version = newVersion;
  writeFileSync(packagePath, `${JSON.stringify(pkg, null, 2)}\n`);
  return newVersion;
}

try {
  const pyVersion = updatePythonVersion();
  const tsVersion = updateTypeScriptVersion();
  console.log("✅ Versions bumped successfully:");
  console.log(`Python: ${pyVersion}`);
  console.log(`TypeScript: ${tsVersion}`);
} catch (error) {
  console.error("❌ Failed to bump versions:", error);
  process.exit(1);
}
