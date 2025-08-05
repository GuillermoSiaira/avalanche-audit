// scripts/analyze_flow.js
const fs = require('fs');
const fetch = require('node-fetch');

const CONTRACT_PATH = "D:/projects/avalanche-audit/contracts/Grader5.sol";
const DEEPSEEK_URL = "http://127.0.0.1:11434/api/generate"; // Endpoint de Ollama
const MODEL = "deepseek-coder:6.7b";

// === Paso 1: Leer contrato ===
console.log(`📄 Reading contract from: ${CONTRACT_PATH}`);
const contractCode = fs.readFileSync(CONTRACT_PATH, 'utf8');

// === Paso 2: Enviar a DeepSeek ===
(async () => {
    console.log("📤 Sending contract to DeepSeek for analysis...");

    const body = {
        model: MODEL,
        prompt: `Analyze this Solidity contract for potential vulnerabilities and explain:\n\n${contractCode}`,
        stream: true
    };

    const response = await fetch(DEEPSEEK_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body)
    });

    if (!response.ok) {
        console.error("❌ Error connecting to DeepSeek:", await response.text());
        return;
    }

    console.log("📥 Receiving response from DeepSeek...\n");

    let finalResponse = "";
    let tokenCount = 0;

    for await (const chunk of response.body) {
        try {
            const lines = chunk.toString().split("\n").filter(line => line.trim() !== "");
            for (const line of lines) {
                const data = JSON.parse(line);

                if (data.response) {
                    process.stdout.write(data.response); // Mostrar en vivo
                    finalResponse += data.response;
                    tokenCount++;
                }

                if (data.done) {
                    console.log(`\n\n✅ DeepSeek Analysis Complete - Tokens received: ${tokenCount}`);
                    console.log("\n=== Final Analysis ===\n");
                    console.log(finalResponse);
                    return;
                }
            }
        } catch (err) {
            // Ignorar fragmentos corruptos
        }
    }
})();
