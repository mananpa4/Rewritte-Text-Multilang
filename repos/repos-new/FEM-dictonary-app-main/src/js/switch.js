const body = document.body;
const userThemePreference = localStorage.getItem("dictionary_color_theme");
const toggleSwitch = document.getElementById("toggle-switch");

toggleSwitch.addEventListener("click", toggleButton);

toggleSwitch.addEventListener("keydown", function (event) {
  if (event.code === "Space" || event.code === "Enter") {
    event.preventDefault();
    toggleButton();
  }
});

function toggleButton() {
  // toggle() returns true if the class was added and false if it was removed
  const darkMode = body.classList.toggle("dark-mode");
  localStorage.setItem("dictionary_color_theme", darkMode ? "dark" : "light");
  toggleSwitch.setAttribute("aria-pressed", darkMode.toString());
}

function setThemePreference() {
  const userThemePreference = localStorage.getItem("dictionary_color_theme");
  // darkMode is true if the user has explicitly set the theme to dark,
  // or if the user has not set a preference and the browser or
  // operating system is currently set to dark mode.
  const darkMode =
    userThemePreference === "dark" ||
    (!userThemePreference &&
      window.matchMedia &&
      window.matchMedia("(prefers-color-scheme: dark)").matches);

  body.classList.toggle("dark-mode", darkMode);
  toggleSwitch.setAttribute("aria-pressed", darkMode.toString());
}

setThemePreference();
