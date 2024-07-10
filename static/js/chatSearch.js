document.addEventListener("DOMContentLoaded", function () {
  // Search functionality
  document
    .getElementById("search-field")
    .addEventListener("input", function () {
      let searchTerm = this.value.toLowerCase();

      // First, remove any existing highlights
      let highlights = document.querySelectorAll("#chat-history .highlight");
      highlights.forEach(function (highlight) {
        let text = highlight.parentNode.textContent;
        highlight.parentNode.textContent = text; // Replace the .highlight span with just its text content
      });

      // If search term is empty, show all messages
      if (!searchTerm) {
        let rows = document.querySelectorAll(
          "#chat-history .user-row, #chat-history .ai-row"
        );
        rows.forEach(function (row) {
          row.style.display = "block";
        });
        return;
      }

      // Loop through each message and check if the message contains the search term
      let messages = document.querySelectorAll(
        "#chat-history .user-message, #chat-history .ai-message"
      );
      messages.forEach(function (message) {
        let messageText = message.textContent.toLowerCase();
        if (messageText.includes(searchTerm)) {
          message.parentNode.style.display = "block"; // Show the entire row (either user or AI)
          highlightSearchTerm(message, searchTerm);
        } else {
          message.parentNode.style.display = "none"; // Hide the entire row if it doesn't match
        }
      });
    });

  function highlightSearchTerm(element, searchTerm) {
    let regex = new RegExp(`(${searchTerm})`, "gi");
    let innerHTML = element.textContent.replace(
      regex,
      '<span class="highlight">$1</span>'
    );
    element.innerHTML = innerHTML;
  }
});

// $(document).ready(function() {
//     //Search functionality
//     $("#search-field").on("input", function() {
//         let searchTerm = $(this).val().toLowerCase();

//         // First, remove any existing highlights
//         $("#chat-history .highlight").each(function() {
//             let text = $(this).parent().text();
//             $(this).parent().text(text); // Replace the .highlight span with just its text content
//         });

//         //IF search term is empty, show all messages
//         if (!searchTerm) {
//             $("#chat-history .user-row, #chat-history .ai-row").show();
//             return;
//         }

//         //Loop through each message and check if the message contains the search term
//         $("#chat-history .user-message, #chat-history .ai-message").each(function() {
//             let messageText = $(this).text().toLowerCase();
//             if (messageText.includes(searchTerm)) {
//                 $(this).parent().show(); //Show the entire row (either user or AI)
//                 highlightSearchTerm(this, searchTerm);
//             } else {
//                 $(this).parent().hide(); //Hide the entire row if it doesn't match
//             }
//         });
//     });

//     function highlightSearchTerm(element, searchTerm) {
//         let regex = new RegExp(`(${searchTerm})`, 'gi');
//         let innerHTML = $(element).text().replace(regex, '<span class="highlight">$1</span>');
//         $(element).html(innerHTML);
//     }
// });
