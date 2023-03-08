var headingText = "This is a typing effect.";

		// Get the heading element
		var heading = document.getElementById("text");

		// Function to type out the heading
		function typeHeading() {
			for (var i = 0; i < headingText.length; i++) {
				setTimeout(function() {
					heading.innerHTML += headingText.charAt(i);
				}, i * 100); // Change the speed of typing by changing this value
			}
		}

		// Call the function to type out the heading
		typeHeading();