import { useEffect, useState } from "react";

export type AccentThemeId = "solar" | "jade" | "crimson";

export interface AccentThemeConfig {
  id: AccentThemeId;
  label: string;
  swatch: string;
  vars: Record<string, string>;
}

export const ACCENT_THEMES: Record<AccentThemeId, AccentThemeConfig> = {
  solar: {
    id: "solar",
    label: "Solar Copper",
    swatch: "#f97316",
    vars: {
      "--brand-50": "255 247 237",
      "--brand-100": "255 237 213",
      "--brand-200": "254 215 170",
      "--brand-300": "253 186 116",
      "--brand-400": "251 146 60",
      "--brand-500": "249 115 22",
      "--brand-600": "234 88 12",
      "--brand-700": "194 65 12",
      "--brand-800": "154 52 18",
      "--brand-900": "124 45 18",
      "--brand-950": "67 20 7",
    },
  },
  jade: {
    id: "jade",
    label: "Emerald Jade",
    swatch: "#10b981",
    vars: {
      "--brand-50": "236 253 245",
      "--brand-100": "209 250 229",
      "--brand-200": "167 243 208",
      "--brand-300": "110 231 183",
      "--brand-400": "52 211 153",
      "--brand-500": "16 185 129",
      "--brand-600": "5 150 105",
      "--brand-700": "4 120 87",
      "--brand-800": "6 95 70",
      "--brand-900": "6 78 59",
      "--brand-950": "2 44 34",
    },
  },
  crimson: {
    id: "crimson",
    label: "Ruby Rose",
    swatch: "#f43f5e",
    vars: {
      "--brand-50": "255 241 242",
      "--brand-100": "255 228 230",
      "--brand-200": "254 205 211",
      "--brand-300": "253 164 175",
      "--brand-400": "251 113 133",
      "--brand-500": "244 63 94",
      "--brand-600": "225 29 72",
      "--brand-700": "190 18 60",
      "--brand-800": "159 18 57",
      "--brand-900": "136 19 55",
      "--brand-950": "76 5 25",
    },
  },
};

const THEME_STORAGE_KEY = "vertexerp_accent_theme";

export function applyAccentTheme(themeId: AccentThemeId) {
  const cfg = ACCENT_THEMES[themeId] || ACCENT_THEMES.solar;
  if (typeof document !== "undefined") {
    const root = document.documentElement;
    Object.entries(cfg.vars).forEach(([k, v]) => root.style.setProperty(k, v));
  }
  try {
    localStorage.setItem(THEME_STORAGE_KEY, cfg.id);
  } catch {
    // ignore storage errors
  }
}

export function useAccentTheme() {
  const [themeId, setThemeId] = useState<AccentThemeId>(() => {
    try {
      const saved = localStorage.getItem(THEME_STORAGE_KEY) as AccentThemeId | null;
      return saved && ACCENT_THEMES[saved] ? saved : "solar";
    } catch {
      return "solar";
    }
  });

  useEffect(() => {
    applyAccentTheme(themeId);
  }, [themeId]);

  return {
    themeId,
    setTheme: (id: AccentThemeId) => {
      setThemeId(id);
      applyAccentTheme(id);
    },
    themes: Object.values(ACCENT_THEMES),
  };
}
