// allows the user to see their password
const passwordViewToggle = $("#togglePassword");
$(passwordViewToggle).click(function () {
  // get the current type of the input box
  const currentType = $("#password").attr("type");

  // if the current type is password {switch to text} else {leave as password};
  $("#password").attr("type", currentType === "password" ? "text" : "password");
  $(".test-pass").attr(
    "type",
    currentType === "password" ? "text" : "password"
  );

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
        headers: {
          "X-CSRFToken": $("input[name='csrf_token']").val(),
        },
        data: JSON.stringify({
          task_id: taskId,
        }),

        success: function (response) {
          // If the server responds with success, fade out and remove the task card
          taskCard.fadeOut(1000, function () {
            // remove it from the dom
            $(this).remove();

            try {
              // Define a mapping of response properties to their corresponding heading IDs
              // object
              const taskMappings = {
                due_today_tasks: "#due-today-heading",
                due_this_week_tasks: "#due-this-week-heading",
                task_list_tasks: "#due-later-heading",
                overdue_tasks: "#overdue-heading",
              };

              // Loop over each task list in the mapping
              // Object.entries being similar to zip() in python
              // key difference being it takes an object and turns it into a list

              // Object.entries(taskMappings)) will return:
              // [["due_today_tasks", "#due-today-heading"], ["due_this_week_tasks", "#due-this-week-heading"], ["task_list_tasks", "#due-later-heading"]]
              for (const [taskList, headingId] of Object.entries(
                taskMappings
              )) {
                if (
                  // check if the taskList's actually exist
                  // e.g. does is "due_today_tasks" in the response sent by flask
                  response.hasOwnProperty(taskList) &&
                  response[taskList] === 0
                ) {
                  $(headingId).css("display", "none");
                }
              }

              console.log(response);
            } catch (error) {
              console.log(error);
            }

            console.log(response);
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
    $(".mobile-navbar a").each(function () {
      var navItem = $(this);
      // Check if the href of the nav item matches the current page
      if (navItem.attr("href") === window.location.pathname) {
        // Remove active class from all and add to the current one
        $(".mobile-navbar a").removeClass("navbar-active");
        navItem.addClass("navbar-active");
      }
    });
  }
  // Run on page load
  updateActiveNavItem();
  updateMobileActiveNav();

  function showMobileNavBar() {
    // get the menu icon
    var menuIcon = $(".mobile-navbar i");
    var mobileNavbarContainer = $(".mobile-navbar-container");

    menuIcon.click(function () {
      // Toggle the visibility of the mobile navigation bar with a sliding animation
      mobileNavbarContainer.slideToggle();

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

  // Selecting all elements with the 'theme' class for event handling
  var themes = $(".theme");

  // Function to switch the website theme
  function switchTheme(theme) {
    // Update CSS variables to reflect the chosen theme
    document.documentElement.style.setProperty(
      "--primary-color",
      `var(--${theme})`
    );
    document.documentElement.style.setProperty(
      "--hover-color",
      `var(--${theme}-hover)`
    );
    document.documentElement.style.setProperty(
      "--task-card-hover-color",
      `var(--${theme}-task-card-hover)`
    );
    document.documentElement.style.setProperty(
      "--primary-success-flash-colour",
      `var(--${theme}-flash)`
    );

    // Save the theme to Local Storage for persistence
    localStorage.setItem("theme", theme);

    // Remove 'active-theme' class from all theme buttons and set it to the current one
    themes.removeClass("active-theme");
    $(`.theme[data-theme="${theme}"]`).addClass("active-theme");
  }

  // Attempt to retrieve and apply the saved theme when the page loads
  var savedTheme = localStorage.getItem("theme");
  if (savedTheme) {
    switchTheme(savedTheme);
  }

  // Event handler for theme buttons
  themes.on("click", function () {
    // Retrieve the theme data attribute from the clicked button
    var theme = $(this).data("theme");
    // Apply the selected theme
    switchTheme(theme);
  });
});
