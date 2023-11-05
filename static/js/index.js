// allows the user to see their password
const passwordViewToggle = $("#togglePassword");
$(passwordViewToggle).click(function () {
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

// once the doc has loaded
$(document).ready(function () {
    // checks if theres any change to a checkbox
    $(".task-checkbox").change(function () {
        // if there is a change then check if its checked
        if ($(this).is(":checked")) {
            // play the animation
            $(this).closest(".task-card").animate({ opacity: "0.1" });
        } else {
            // if its not checked then bring it back
            $(this).closest(".task-card").animate({ opacity: "1" });
        }
    });
    
    // Function to update the active class based on the current body ID
    function updateActiveNavItem() {
        var currentPage = $("body").attr("id"); // Get the unique ID of the body tag
        // Loop through all nav links
        $(".navbar-full a").each(function () {
            var navItem = $(this);
            // Check if the href of the nav item matches the current page
            if (navItem.attr("href") === window.location.pathname) {
                // Remove active class from all and add to the current one
                $(".navbar-full a").removeClass("navbar-active");
                navItem.addClass("navbar-active");
            }
        });
    }
    
    // Run on page load
    updateActiveNavItem();
});
