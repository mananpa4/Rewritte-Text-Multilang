const body = document.querySelector("body");
const currentFont = document.querySelector(".dropdown__button span");
const storedFont = localStorage.getItem("preferredFont");

function configFont() {
  if (!storedFont) {
    changeFont("'Inter', sans-serif", "Sans Serif");
    return;
  }

  const { fontFamily, fontAlias } = JSON.parse(storedFont);
  changeFont(fontFamily, fontAlias);
}

function changeFont(fontFamily, fontAlias) {
  currentFont.textContent = fontAlias;
  body.style.fontFamily = fontFamily;
}

const fontButtons = document.querySelectorAll(".dropdown__menu-item button");
fontButtons.forEach((button) => {
  button.addEventListener("click", function () {
    const fontFamily = this.getAttribute("data-font");
    const fontAlias = this.getAttribute("data-font-alias");
    const storageItem = JSON.stringify({ fontFamily, fontAlias });
    localStorage.setItem("preferredFont", storageItem);
    changeFont(fontFamily, fontAlias);
  });
});

configFont();
