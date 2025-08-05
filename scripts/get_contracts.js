const fs = require("fs");
const axios = require("axios");

async function main() {
  console.log("[1] Starting get_contracts.js...");

  // Example contract URL (can be replaced with real source)
  const contractUrl = "https://raw.githubusercontent.com/OpenZeppelin/openzeppelin-contracts/master/contracts/token/ERC20/ERC20.sol";

  console.log("[2] Attempting to download contract from:", contractUrl);

  try {
    // Adding a timeout to avoid hanging indefinitely
    const response = await axios.get(contractUrl, { timeout: 10000 });
    console.log("[3] Download successful. Size:", response.data.length, "bytes");

    const savePath = "./contracts/ERC20.sol";
    fs.writeFileSync(savePath, response.data);
    console.log("[4] Contract saved at:", savePath);

  } catch (error) {
    console.error("[ERROR] Failed to download the contract:");
    console.error(error.message);
  }

  console.log("[5] Script finished.");
  process.exit(0);
}

main();
