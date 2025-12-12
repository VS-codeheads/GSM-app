import js from "@eslint/js";
import globals from "globals";
import { defineConfig } from "eslint/config";

// ESLint Flat Config (ESLint v9+)

export default [
  {
    files: ["**/*.js"],

    languageOptions: {
      ecmaVersion: "latest",
      sourceType: "script",
      globals: {
        window: "readonly",
        document: "readonly",
        console: "readonly",
        $: "readonly",       // jQuery support
      }
    },

    rules: {
      ...js.configs.recommended.rules,

      "no-unused-vars": "warn",
      "no-undef": "warn",
      "semi": ["error", "always"],
      "quotes": ["error", "double"],
      "no-mixed-spaces-and-tabs": "warn"
    }
  }
];
