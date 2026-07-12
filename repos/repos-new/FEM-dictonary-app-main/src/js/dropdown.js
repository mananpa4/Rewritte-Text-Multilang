const dropdown = document.querySelector(".dropdown");
const button = dropdown.querySelector(".dropdown__button");
const menu = dropdown.querySelector(".dropdown__menu");

function toggleDropdown() {
  const isOpen = dropdown.classList.toggle("dropdown--open");
  dropdown.setAttribute("aria-expanded", isOpen.toString());
  menu.setAttribute("aria-hidden", (!isOpen).toString());
}

function handleButtonKeydown(event) {
  const { code } = event;
  if (code === "Space" || code === "Enter") {
    event.preventDefault();
    toggleDropdown();
  } else if (code === "Escape") {
    closeDropdown();
  }
}

function handleMenuKeydown(event) {
  const { code } = event;
  if (code === "Escape") {
    closeDropdown();
  }
}

function closeDropdown() {
  dropdown.classList.remove("dropdown--open");
  dropdown.setAttribute("aria-expanded", "false");
  menu.setAttribute("aria-hidden", "true");
  button.focus();
}

button.addEventListener("click", toggleDropdown);
button.addEventListener("keydown", handleButtonKeydown);
menu.addEventListener("keydown", handleMenuKeydown);
