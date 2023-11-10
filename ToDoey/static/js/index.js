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
    var taskCard = $(this).closest(".task-card");
    if ($(this).is(":checked")) {
      // grab the id number
      var taskId = $(this).data("id"); // when using .data() you only need the ending and DO NOT need to put "data-id" (:
      $.ajax({
        url: "/update_task",
        type: "POST",
        contentType: "application/json",
        data: JSON.stringify({
          task_id: taskId,
        }),
        success: function (response) {
          // If the server responds with success, fade out and remove the task card
          taskCard.fadeOut(1000, function () {
            // remove it from the dom
            $(this).remove();
          });
        },
        else(error) {
          console.log(error);
        },
      });
    } else {
      // if its not checked then bring it back
      // the user wont really have time to press the button again.
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

  function updateMobileActiveNav() {
    var currentPage = $("body").attr("id"); // Get the unique ID of the body tag
    // Loop through all nav links
    $(".movile-navbar a").each(function () {
      var navItem = $(this);
      // Check if the href of the nav item matches the current page
      if (navItem.attr("href") === window.location.pathname) {
        // Remove active class from all and add to the current one
        $(".movile-navbar a").removeClass("navbar-active");
        navItem.addClass("navbar-active");
      }
    });
  }
  // Run on page load
  updateActiveNavItem();
  updateMobileActiveNav();

  function showMobileNavBar() {
    // get the menu icon
    var menuIcon = $(".movile-navbar i");

    menuIcon.click(function () {
      $(".mobile-navbar-container").toggleClass("mobile-navbar-container-show");

      // change the icon menu from list to cross and vice versa
      if (menuIcon.hasClass("bi-list")) {
        menuIcon.removeClass("bi-list");
        menuIcon.addClass("bi-x");
      } else {
        menuIcon.addClass("bi-list");
        menuIcon.removeClass("bi-x");
      }
    });
  }
  showMobileNavBar();
});
