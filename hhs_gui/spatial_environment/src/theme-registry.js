export const THEMES = Object.freeze([
  { id: "cyan-blue", label: "Cyan Blue", colors: ["#45caff", "#8b5cff", "#b2f6ff"], background: "#020712" },
  { id: "violet-magenta", label: "Violet Magenta", colors: ["#d65cff", "#6e7cff", "#ffd0ff"], background: "#090311" },
  { id: "emerald-gold", label: "Emerald Gold", colors: ["#41e5a4", "#e8c65d", "#d8ffe9"], background: "#03100d" },
  { id: "amber-red", label: "Amber Red", colors: ["#ff874a", "#ff3f65", "#ffe2d5"], background: "#110604" },
  { id: "arctic-silver", label: "Arctic Silver", colors: ["#bce9ff", "#aeb8d4", "#ffffff"], background: "#04070c" },
  { id: "minimal-dark", label: "Minimal Dark", colors: ["#e8e8e8", "#9da8b5", "#ffffff"], background: "#08090b" },
  { id: "minimal-light", label: "Minimal Light", colors: ["#175da8", "#6c35a6", "#08233d"], background: "#eaf4fb", light: true }
]);

export function themeById(id) {
  return THEMES.find((theme) => theme.id === id) ?? THEMES[0];
}

export function customTheme(colors, background = "#020712") {
  return { id: "custom", label: "Custom", colors, background };
}
