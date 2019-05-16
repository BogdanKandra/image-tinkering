"use strict";

// For each result file, creates a container holding the file and a revealing "SAVE" button over the file
function populateResultsContainer(data) {

	let resultsContainer = $('#resultsContainer')

	for (const name of data) {

		// Build the img element to be displayed
		let path = '../static/tempdata/' + name
		let image = $('<img>').addClass('hoverable_image')
		image.prop('src', path)
		image.prop('alt', 'Image Preview not Available')
		image.prop('height', '200')

		// Build the div holding the revealing "SAVE" button
		let saveDiv = $('<div>').addClass('configure_container')
		let saveButton = $('<button>').addClass('ui primary button')
		saveButton.html('SAVE')
		saveButton.click(function() {
            saveFile(path)
        })
		saveDiv.append(saveButton)

		// Build the containing div
		let container = $('<div>').addClass('hoverable_container')
		container.append(image).append(saveDiv)

		resultsContainer.append(container)
	}
}

// Downloads the file to the 'downloads' directory of the user
function saveFile(path) {

    let download_name = path.substring(path.lastIndexOf("/") + 1).split("_")[0] + "_processed"
    let link = $('<a>')
    link.prop('href', path)
    link.prop('download', download_name)
    link[0].click()
}
