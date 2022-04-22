ThemeChanger.themes = {
    os: {
        name: "OS",
        css: null,
    },
    light: {
        name: "Light",
        css: [
            ["color-scheme", "light"],
            ["--font-dark", "var(--font-dark--light)"],
            ["--font-light", "var(--font-light--light)"],
            ["--bg-bnt", "var(--bg-bnt--light)"],
            ["--bg-body", "var(--bg-body--light)"],
            ["--bg-sub-body", "var(--bg-sub-body--light)"],
            ["--bg-panel", "var(--bg-panel--light)"],
        ]
    },
    dark: {
        name: "Dark",
        css: [
            ["color-scheme", "dark"],
            ["--font-dark", "var(--font-dark--dark)"],
            ["--font-light", "var(--font-light--dark)"],
            ["--bg-bnt", "var(--bg-bnt--dark)"],
            ["--bg-body", "var(--bg-body--dark)"],
            ["--bg-sub-body", "var(--bg-sub-body--dark)"],
            ["--bg-panel", "var(--bg-panel--dark)"],
        ]
    },
};

ThemeChanger.theme_picker_parent = document.querySelector("main");
ThemeChanger.use_local = true;
ThemeChanger.selected_theme_css_class = "green";

document.getElementById("themeToggleBnt").addEventListener("click", ThemeChanger.toggle_theme_picker);

ThemeChanger.on_load();
