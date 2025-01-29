function showAlert(message, type) {
    const alertBox = document.getElementById('customAlert');
    alertBox.classList.remove('alert-success', 'alert-error', 'alert-info', 'alert-warning');
    alertBox.classList.add(type);
    alertMessage.innerText = message;

    document.getElementById("customAlert").style.display = "block";
    setTimeout(() => {
        closeAlert()
}, 4000);
}
function closeAlert() {
    document.getElementById("customAlert").style.display = "none";
}