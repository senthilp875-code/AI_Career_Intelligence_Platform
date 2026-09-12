console.log("TalentIQ Dashboard JS loaded");

document.addEventListener("DOMContentLoaded", function () {

    console.log("Dashboard DOM loaded");

    const personalityBtn =
        document.querySelector("#personalityDetailsBtn");

    const personalityDetails =
        document.querySelector("#personalityDetails");

    console.log("Button:", personalityBtn);
    console.log("Details:", personalityDetails);

    if (!personalityBtn || !personalityDetails) {
        console.log("Personality elements not found");
        return;
    }

    personalityBtn.addEventListener("click", function () {

        const isHidden =
            personalityDetails.style.display === "none" ||
            personalityDetails.style.display === "";

        if (isHidden) {

            personalityDetails.style.display = "block";

            personalityBtn.innerHTML = `
                Hide Details
                <i class="fas fa-arrow-up"></i>
            `;

        } else {

            personalityDetails.style.display = "none";

            personalityBtn.innerHTML = `
                Know More About You
                <i class="fas fa-arrow-right"></i>
            `;

        }

    });

});
document.addEventListener("DOMContentLoaded", function () {

    const profileDropdown = document.querySelector(".profile-dropdown");
    const profileBtn = document.querySelector(".profile-btn");

    if (profileDropdown && profileBtn) {

        profileBtn.addEventListener("click", function (event) {

            event.stopPropagation();

            profileDropdown.classList.toggle("active");

        });

        document.addEventListener("click", function (event) {

            if (!profileDropdown.contains(event.target)) {

                profileDropdown.classList.remove("active");

            }

        });

    }

});