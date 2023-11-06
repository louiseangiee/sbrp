// application_history.js
document.addEventListener("DOMContentLoaded", function () {
    // Get a reference to the table body
    const tableBody = document.querySelector(".table tbody");

    // Function to populate the table with application history data
    function populateTable(data) {
        const applicationHistory = data.application_history; // Access the application history array

        // Clear existing table rows
        tableBody.innerHTML = "";

        // Loop through the application history data and create table rows
        applicationHistory.forEach((application, index) => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <th class="align-middle" scope="row">${index + 1}</th>
                <td class="align-middle">${application.staff_name}</td>
                <td class="align-middle">${application.role_name}</td>
                <td class="align-middle">${application.applied_date}</td>
                <td class="align-middle">
                    <div class="d-flex align-items-center">
                        <span style="margin-right: 5px;">${application.status}</span>
                        <button id="cancelButton" type="button" class="btn btn-danger cancel-button" data-bs-target="#verticalycentered" data-application-id="${application.application_id}">Cancel</button>
                    </div>
                </td>
            `;

            // Append the row to the table body
            tableBody.appendChild(row);

            // Add a click event listener to the Cancel button
            const cancelButton = row.querySelector(".cancel-button");
            cancelButton.addEventListener("click", function () {
                const applicationId = cancelButton.getAttribute("data-application-id");

                if (applicationId) {
                    // Call your cancel application function with the application ID
                    cancelApplication(applicationId);
                } else {
                    // Handle the case where applicationId is not found
                    alert("Application ID not found.");
                }
            });
        });
    }

    // Function to send an HTTP DELETE request to cancel an application
    function cancelApplication(applicationId) {
        // Define the URL of your Flask route
        const url = `/delete_application/${applicationId}`;

        // Send an HTTP DELETE request using the Fetch API
        fetch(url, {
            method: "DELETE",
        })
            .then((response) => {
                if (response.status === 200) {
                    // Application was deleted successfully
                    alert("Application deleted successfully");
                    // You can also remove the associated HTML element if needed
                    // button.parentElement.parentElement.remove();
                    // Or simply refresh the page to update the table
                    location.reload();
                } else if (response.status === 404) {
                    // Application not found
                    alert("Application not found. It may have already been deleted.");
                } else if (response.status === 400) {
                    // Application past the deadline
                    alert("Application cannot be deleted as it's past the deadline.");
                } else {
                    // Handle other errors
                    alert("Error deleting application. Please try again later.");
                }
            })
            .catch((error) => {
                console.error("Error:", error);
                alert("An unexpected error occurred while deleting the application.");
            });
    }

    // Make an AJAX request to retrieve application history data
    fetch("/get_application_history") // Replace 19 with the actual staff_id
        .then((response) => {
            if (response.status === 200) {
                return response.json();
            } else {
                throw new Error("Error fetching application history data");
            }
        })
        .then((data) => {
            console.log("application_History:", data)
            // Populate the table with the retrieved data
            populateTable(data);
        })
        .catch((error) => {
            console.error("Error:", error);
        });
});
