// Wait for the DOM to be fully loaded
document.addEventListener("DOMContentLoaded", function () {
  fetch("/skills")
    .then((response) => response.json())
    .then((data) => {
      // Access and render the skills data in the skills card
      const skillsCard = document.getElementById("skillsAccordion");
      const skillsNameList = data.data.skill_names;
      const skillsDescList = data.data.descriptions;
      const accordionId = "skillsAccordion";

      skillsNameList.forEach((skill, index) => {
        const uniqueId = "collapse" + index;
        const skillCard = document.createElement("div");
        skillCard.classList.add("accordion-item");

        skillCard.innerHTML = `
          <h2 class="accordion-header">
            <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#${uniqueId}" aria-expanded="true" aria-controls="${uniqueId}">
              <strong>${skill}</strong>
            </button>
          </h2>
          <div id="${uniqueId}" class="accordion-collapse collapse" data-bs-parent="#${accordionId}">
            <div class="accordion-body">
             ${skillsDescList[index]}
            </div>
          </div>
        `;

        skillsCard.appendChild(skillCard);
      });
    })
    .catch((error) => console.error("Error:", error));
});
