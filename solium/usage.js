import solium from "solium"
import fs from "fs"

const source = fs.readFileSync("./contracts/check.sol")

const errors = solium.lint(source, {
    "extends": "solium:recommended",
    "plugins": ["security"],
    "rules": {
            "quotes": ["error", "double"],
            "double-quotes": [2],   // returns a rule deprecation warning
            "pragma-on-top": [1]
    },

    "options": { "returnInternalIssues": true }
})

errors.forEach(element => {
    console.log(element)
});