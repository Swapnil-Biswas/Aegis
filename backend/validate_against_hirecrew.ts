import fs from "node:fs";
import path from "node:path";
import {
  sellerLocalSubmissionGuide,
  sellerLocalDeploymentContract,
  sellerLocalResearchBenchmarkPack,
  validateSellerLocalResearchResult,
  validateSellerLocalDeploymentManifest
} from "../../../HireCrew/platform/src/mcp/seller-local.js";

console.log("=== HIRECREW SELLER-LOCAL BUILDER KIT SELF-TEST ===");

// 1. Get Submission Guide
const guide = sellerLocalSubmissionGuide();
console.log("\n[1] Submission Guide Version:", guide.version);
console.log("    Rule:", guide.submissionRule);

// 2. Get Seller API Contract
const contract = sellerLocalDeploymentContract();
console.log("\n[2] Seller API Contract Version:", contract.version);
console.log("    Submit Method:", contract.submit.method);
console.log("    Poll Method:", contract.poll.method);

// 3. Get Benchmark Pack
const pack = sellerLocalResearchBenchmarkPack();
console.log("\n[3] Research Benchmark Pack:", pack.suiteVersion);
console.log("    Total Cases:", pack.cases.length);

// 4. Validate All 5 Benchmark Cases
const candidatePaths = [
  path.resolve(__dirname, "app/data/hirecrew_benchmark_outputs.json"),
  path.resolve("./backend/app/data/hirecrew_benchmark_outputs.json"),
  path.resolve("./aegis/backend/app/data/hirecrew_benchmark_outputs.json")
];
const dataFile = candidatePaths.find(p => fs.existsSync(p)) || candidatePaths[0];
const outputs = JSON.parse(fs.readFileSync(dataFile, "utf-8"));

console.log("\n[4] Validating AEGIS Outputs Against HireCrew Rubric:");
let allPassed = true;

for (const caseItem of pack.cases) {
  const generated = outputs[caseItem.id];
  if (!generated) {
    console.error(`❌ Missing generated output for case: ${caseItem.id}`);
    allPassed = false;
    continue;
  }

  const validation = validateSellerLocalResearchResult({
    caseId: caseItem.id,
    result: generated.result
  });

  if (validation.status === "structural_pass") {
    console.log(`    ✅ Case "${caseItem.id}": STRUCTURAL PASS (0 findings)`);
  } else {
    console.error(`    ❌ Case "${caseItem.id}": FAIL -> Findings:`, validation.findings);
    allPassed = false;
  }
}

// 5. Validate Deployment Manifest
console.log("\n[5] Validating AEGIS Seller Deployment Manifest:");
const manifestInput = {
  title: "AEGIS — AI Text Forensics & Attribution",
  description: "Advanced empirical forensic intelligence agent that analyzes written content across statistical, neural, stylometric, and discourse layers to detect AI generation, human writing, and hybrid compositions.",
  endpoint: "https://aegis-forensics.antigravity.run/jobs",
  output: {
    quantity: 1,
    unit: "Forensic Analysis Report",
    summary: "Comprehensive forensic audit report with calibrated AI-likelihood, passage-level heatmap, and primary source citations.",
    deliveryEstimate: "30 seconds"
  },
  source: {
    repository: "https://github.com/Swapnil-Biswas/Aegis",
    commit: "7260efded3c46c7b6c35b3f636992550cfccca2e"
  }
};

try {
  const manifestResult = validateSellerLocalDeploymentManifest(manifestInput);
  console.log("    ✅ Manifest Status:", manifestResult.status);
  console.log("    Listing Title:", manifestResult.listing.title);
  console.log("    Endpoint:", manifestResult.endpoint);
  console.log("    Repository:", manifestResult.listing.source?.repository);
  console.log("    Next Step:", manifestResult.nextStep);
} catch (err: any) {
  console.error("    ❌ Manifest Validation Failed:", err.message);
  allPassed = false;
}

if (allPassed) {
  console.log("\n🎯 ALL HIRECREW BUILDER KIT SELF-TESTS PASSED PERFECTLY!\n");
} else {
  console.error("\n⚠️ SOME CHECKS FAILED.\n");
  process.exit(1);
}
