const root = document.documentElement;
root.classList.add('hhs-harmonic-studio-theme');

for (const [href, marker] of [
  ['./src/harmonic-studio-theme.css', 'hhs-harmonic-theme'],
  ['./src/integrated-workbench.css', 'hhs-integrated-workbench'],
  ['./src/integrated-assistant.css', 'hhs-integrated-assistant'],
  ['./src/intuitive-ide.css', 'hhs-intuitive-ide'],
]) {
  if (document.querySelector(`link[data-${marker}]`)) continue;
  const link = document.createElement('link');
  link.rel = 'stylesheet';
  link.href = href;
  link.dataset[marker.replace(/-([a-z])/g, (_, letter) => letter.toUpperCase())] = 'true';
  document.head.append(link);
}

const themeColor = document.querySelector('meta[name="theme-color"]');
if (themeColor) themeColor.content = '#1a130e';

window.HHSThemeBootstrap = Object.freeze({
  schema: 'HHS_HARMONIC_STUDIO_THEME_BOOTSTRAP_V3',
  theme: 'WARM_CHARCOAL_AMBER_GOLD',
  static_layout_replaced: false,
  integrated_workbench_css_independent: true,
  integrated_assistant_css_independent: true,
  intuitive_ide_css_independent: true,
  frontend_is_authority: false,
});
