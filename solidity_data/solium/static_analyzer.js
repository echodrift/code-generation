const RULES = {
    "extends": "solium:recommended",
    "plugins": ["security"],
    "rules": {
            "quotes": ["error", "double"],
            "double-quotes": [2],   // returns a rule deprecation warning
            "pragma-on-top": 1
    },
}