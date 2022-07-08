"use-strict";

ThemeChanger.theme_picker_parent = document.querySelector("main");
ThemeChanger.use_local = true;
ThemeChanger.selected_theme_css_class = "ok";

let themeToggleBnt = document.getElementById("themeToggleBnt")
themeToggleBnt.addEventListener("click", ThemeChanger.toggle_theme_picker);
themeToggleBnt.classList.remove("hidden");

ThemeChanger.on_load();
