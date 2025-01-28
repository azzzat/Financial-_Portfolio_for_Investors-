// JavaScript to handle form validation before submission
document.querySelector("form").addEventListener("submit", function(event) {
    let userInput = document.getElementById("user_input").value;
    if (userInput.trim() === "") {
        alert("Please enter some text");
        event.preventDefault();  // Prevent form submission if input is empty
    }
});