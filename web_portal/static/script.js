ThemeChanger.themes = {
    os: {
        name: "OS",
        css: null,
    },
    light: {
        name: "Light",
        css: [
            ["color-scheme", "light"],
            ["--font-dark", "black"],
            ["--font-light", "#f0f0f0"],
            ["--bg-bnt", "#adadad"],
            ["--bg-body", "#9299a5"],
            ["--bg-sub-body", "#8c93a0"],
            ["--bg-panel", "#848a94"],
        ]
    },
    dark: {
        name: "Dark",
        css: [
            ["color-scheme", "dark"],
            ["--font-dark", "var(--font-light)"],
            ["--font-light", "#bcbcbc"],
            ["--bg-bnt", "#003d4b"],
            ["--bg-body", "#002b36"],
            ["--bg-sub-body", "#073540"],
            ["--bg-panel", "#083b47"],
        ]
    },
};

ThemeChanger.theme_picker_parent = document.querySelector("main");
ThemeChanger.use_local = true;
ThemeChanger.selected_theme_css_class = "green";

document.getElementById("themeToggleBnt").addEventListener("click", ThemeChanger.toggle_theme_picker);

ThemeChanger.on_load();
