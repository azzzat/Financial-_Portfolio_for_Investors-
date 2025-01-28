// JavaScript to handle form validation before submission
document.querySelector("form").addEventListener("submit", function(event) {
    let userInput = document.getElementById("user_input").value;
    if (userInput.trim() === "") {
        alert("Please enter some text");
        event.preventDefault();  // Prevent form submission if input is empty
    }
});

document.addEventListener("DOMContentLoaded", () => {
    const fetchAnalyticsButton = document.getElementById("fetch-analytics");
    const analyticsDiv = document.getElementById("analytics");
    const analyticsDataDiv = document.getElementById("analytics-data");

    fetchAnalyticsButton.addEventListener("click", () => {
        fetch("/api/portfolio_analytics")
            .then(response => response.json())
            .then(data => {
                analyticsDiv.style.display = "block";

                const analyticsHTML = `
                    <p><strong>Total Portfolio Value:</strong> $${data.total_value.toFixed(2)}</p>
                    <p><strong>Daily Change (%):</strong> ${data.daily_change}%</p>
                    <h3>Top Performers</h3>
                    <table>
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>ROI (%)</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${data.top_performers.map(asset => `
                                <tr>
                                    <td>${asset.name}</td>
                                    <td>${asset.roi}%</td>
                                </tr>
                            `).join("")}
                        </tbody>
                    </table>
                `;

                analyticsDataDiv.innerHTML = analyticsHTML;
            })
            .catch(error => {
                analyticsDiv.style.display = "block";
                analyticsDataDiv.innerHTML = `<p style="color: red;">Failed to fetch analytics. Try again later.</p>`;
                console.error("Error fetching analytics:", error);
            });
    });
});