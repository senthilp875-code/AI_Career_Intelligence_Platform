document.addEventListener("DOMContentLoaded", () => {

    const button = document.querySelector(".login-btn");

    button.addEventListener("click", () => {

        button.innerHTML = "⏳ Signing In...";

    });

});