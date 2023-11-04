// allows the user to see their password
const passwordViewToggle = $("#togglePassword");
$(passwordViewToggle).click(function() {
    // get the current type of the input box
    const currentType = $("#password").attr("type");
    
    // if the current type is password {switch to text} else {leave as password};
    $("#password").attr("type", currentType === "password" ? "text" : "password");
    
    // toggle the opacity class
    $(this).toggleClass("active");

    // toggle the icon classes
    if ($(this).hasClass("bi-eye")) {
        $(this).removeClass("bi-eye").addClass("bi-eye-slash");
    } else {
        $(this).removeClass("bi-eye-slash").addClass("bi-eye");
    }
    
});
