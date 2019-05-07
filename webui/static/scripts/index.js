"use strict";

let imageCapture // Reference used for capturing images

// Attach handlers on document ready
$(document).ready(function() {

	let fileInput = $('#fileInput')
	let uploadButton = $('#uploadInput')

	// Display relevant information depending on the number of selected files
	fileInput.change(function(event) {

		let countParagraph = $('#filesCount')
		let fileNames = $('#fileNames')
		let filesSource = $('#filesSource')
		let filesContainer = $('#filesContainer')
		let steps = $('#steps')
		let filesCount = event.target.files.length

		// Remove existing file names and images, if user reselects files
		fileNames.empty()
		filesContainer.empty()
		filesSource.text('Disk')

		if (filesCount != 0) {
			uploadButton.removeClass('disabled')
			countParagraph.html('Files Loaded: ' + filesCount) // TODO - Style this to be civilised

			for (let i = 0; i < filesCount; i++) {
				let fileName = $('<span>').text(event.target.files[i]['name'] + ' ') // TODO - Change to tags
				fileNames.append(fileName)

				let imageElement = $('<img>')
				imageElement.prop('src', URL.createObjectURL(event.target.files[i]))
				imageElement.prop('alt', 'Image Preview not Available')
				imageElement.prop('height', '200')

				filesContainer.append($('<div>').append(imageElement))
			}

			steps.css('position', 'absolute')
		} else {
			uploadButton.addClass('disabled')
			countParagraph.html('No Files loaded yet')
			steps.css('position', 'fixed')
		}
	})
})

// Initialises and opens the image capture modal
function displaySelfieModal() {

	let actionButtons = $('.actions').first().find('.ui')

	$('#selfieModal').modal({
							onHide: function() {
								actionButtons.first().addClass('disabled')
								// Stop the camera feed if necessary
								if (imageCapture !== undefined && imageCapture.track.readyState != 'ended') {
									imageCapture.track.stop()
								}
							},
							onApprove: function() {
							},
							onDeny: function() {
							}
						}).modal('show')

	// Initialise the camera feed if necessary
	if (imageCapture === undefined || imageCapture.track.readyState == 'ended') {
		navigator.mediaDevices.getUserMedia({video: true})
							.then(mediaStream => {
								document.querySelector('video').srcObject = mediaStream;
								const track = mediaStream.getVideoTracks()[0]
								imageCapture = new ImageCapture(track)
								actionButtons.first().removeClass('disabled')
							})
	}
}

// Initialises and opens the operation configuration modal
function displayConfigurationModal() {

	populateOperationsSelect()
	let operationsSelect = $("[name='operations']")

	$('#configurationModal').modal({
								onHide: function() {    // Called whenever modal is closed
									operationsSelect.dropdown('clear')
								},
								onApprove: function() { // ACCEPT button
									console.log('MODAL APPROVED')
								},
								onDeny: function() {    // CANCEL button

								}
							}).modal('show')
}

// Captures an image from the camera feed
function captureImage() {

	let snapshot = $('#snapshot')
	let cameraFeed = $('#cameraFeed')
	let actionButtons = $('.actions').first().find('.ui')

	if (snapshot.css('display') == 'none') {
		// Capture image and display it
		imageCapture.takePhoto()
					.then(blob => {
						snapshot.prop('src', URL.createObjectURL(blob))
						snapshot.toggle()
						cameraFeed.toggle()
					})

		// Update the action buttons
		actionButtons.first().html('DISCARD')
		actionButtons.eq(1).removeClass('disabled')
	} else {
		// Redisplay the video feed
		snapshot.css('display', 'none')
		cameraFeed.toggle()

		// Update the action buttons
		actionButtons.first().html('SNAP')
		actionButtons.eq(1).addClass('disabled')
	}
}

// Confirms the currently captured image for uploading
function submitImage() {

	let countParagraph = $('#filesCount')
	let fileNames = $('#fileNames')
	let filesSource = $('#filesSource')
	let filesContainer = $('#filesContainer')
	let snapshot = $('#snapshot')
	let uploadButton = $('#uploadInput')

	let imageElement = $('<img>')
	imageElement.prop('src', snapshot.prop('src'))
	imageElement.prop('alt', 'Image Preview not Available')
	imageElement.prop('height', '200')

	countParagraph.html('Files Loaded: 1')
	fileNames.empty()
	fileNames.append('Selfie')
	filesSource.text('Snapshot')
	filesContainer.empty()
	filesContainer.append($('<div>').append(imageElement))
	uploadButton.removeClass('disabled')
}

// Builds the request data and sends it to the AJAX call
function uploadFiles() {
	// Disable the upload button, while the upload is being performed
	let uploadButton = $('#uploadInput')
	uploadButton.addClass('disabled')

	// Build the request data - a list of selected files
	let imageData = new FormData()
	let filesSource = $('#filesSource')

	if (filesSource.text() == 'Disk') {
		// File source is the file input
		const files = $('#fileInput').prop('files')
		for (let i = 0; i < files.length; i++) {
			imageData.append('files-' + (i + 1), files[i])
		}
		uploadAjax(imageData)
	} else {
		// File source is the webcam feed
		let snapshotImg = $('#snapshot')[0]
		let canvas = document.createElement("canvas")
		let context = canvas.getContext("2d")
		canvas.width = snapshotImg.naturalWidth
		canvas.height = snapshotImg.naturalHeight
		context.drawImage(snapshotImg, 0, 0)
		canvas.toBlob(function(blob) {
			imageData.append('files-1', blob, 'Selfie.jpg')
			uploadAjax(imageData)
		})
	}
}

// Actually performs the AJAX call which saves the files and initialises its channel and FFT images
function uploadAjax(imageData) {

	let uploadButton = $('#uploadButton')

	$.ajax({
		url: '/uploads',
		method: 'POST',
		data: imageData,
		processData: false,
		contentType: false,
		success: function(data) {
			new Noty({
				text: 'File Upload Succeeded!',
				type: 'success',
				layout: 'top',
				theme: 'relax',
				timeout: 5000
			}).show()
			
			console.log('>>>>> Data:', data)
			
			// Launch the initialisations procedure
			$.ajax({
				url: '/initialisations/',
				method: 'POST',
				data: JSON.stringify({'files': data}),
				contentType: 'application/json',
				success: function(data) {
					console.log('>>>>> Initialisations successful')
				},
				error: function(request, status, error) {
					console.log('>>>>> Error during initialisations process')
				}
			})

			// Direct the user to the Operation Selection step
			$('#fileSelectionContent').css('display', 'none')
			$('#operationSelectionContent').css('display', 'block')
			$('#steps').children('.step').first().removeClass('active')
			$('#steps').children('.step').first().addClass('completed')
			$('#steps').children('.step').eq(1).addClass('active')

			// Populate the container holding uploaded images
			populateFilesAndOperationsContainer(data)
		},
		error: function(request, status, error) {
			new Noty({
				text: 'File upload failed!',
				type: 'error',
				layout: 'top',
				theme: 'relax',
				timeout: 5000
			}).show()
			
			// Enable the upload button back
			uploadButton.removeClass('disabled')
		}
	})
}

// Switches the application mode between 'Image' and 'Video'
// TODO - Change the page content accordingly (<title>, <h1> title and other stuff)
function changeMode() {

	let visibleContent = $('#switchMode').find('.visible').first()
	let hiddenContentIcon = $('#switchMode').find('.hidden').first().find('.icon').first()

	if (visibleContent.html().includes('VIDEO')) {
		visibleContent.html('SWITCH TO IMAGE MODE')
	} else {
		visibleContent.html('SWITCH TO VIDEO MODE')
	}

	hiddenContentIcon.toggleClass('image')
	hiddenContentIcon.toggleClass('video')
}

// For each uploaded file, creates a container holding the uploaded file and an accordion displaying
// selected operations and parameters
function populateFilesAndOperationsContainer(data) {

	let imageNames = data['image']
	let filesAndOperationsContainer = $('#filesAndOperationsContainer')

	for (const name of imageNames) {

		// Build the img element to be displayed
		let path = '../static/uploads/images/' + name
		let image = $('<img>')
		image.prop('src', path)
		image.prop('alt', 'Image Preview not Available')
		image.prop('height', '200')
		image.addClass('hoverable_image')

		// Build the div holding the revealing "CONFIGURE" button
		let configureDiv = $('<div>')
		configureDiv.addClass('configure_container')
		let configureButton = $('<button>')
		configureButton.addClass('ui primary button')
		configureButton.html('CONFIGURE')
		configureButton.click(displayConfigurationModal)
		configureDiv.append(configureButton)

		// Build the accordion element to be displayed under the img
		// TODO

		// Build the containing div
		let container = $('<div>')
		container.addClass('hoverable_container')
		container.append(image).append(configureDiv)

		filesAndOperationsContainer.append(container)
	}
}

// Function called on pressing the PROCESS button on second screen
function test() {
	console.log('PRESSED BUTTON IN SECOND SCREEN --- PROCESSING...')
}
