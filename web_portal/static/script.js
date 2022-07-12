// @license magnet:?xt=urn:btih:0b31508aeb0634b347b8270c7bee4d411b5d4109&dn=agpl-3.0.txt AGPL-3.0-or-later
"use-strict";

ThemeChanger.theme_picker_parent = document.querySelector("main");
ThemeChanger.use_local = true;
ThemeChanger.selected_theme_css_class = "green";

let themeToggleBnt = document.getElementById("themeToggleBnt")
themeToggleBnt.addEventListener("click", ThemeChanger.toggle_theme_picker);
themeToggleBnt.classList.remove("hidden");

ThemeChanger.on_load();
// @license-end
