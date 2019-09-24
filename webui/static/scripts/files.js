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
			countParagraph.html('Files Loaded: ' + filesCount)

			for (let i = 0; i < filesCount; i++) {
				let fileName = $('<a>').prop('href', '#')
									   .addClass('tagStat tagFile')
									   .text(event.target.files[i]['name'] + ' ')
				fileNames.append(fileName)

				let imageElement = $('<img>')
				imageElement.prop('src', URL.createObjectURL(event.target.files[i]))
				imageElement.prop('alt', 'Image Preview not Available')
				imageElement.prop('height', '200')

				filesContainer.append($('<div>').append(imageElement))
			}
		} else {
			uploadButton.addClass('disabled')
			countParagraph.html('No Files loaded yet')
		}

		if (filesCount > 1) {
			steps.css('position', 'absolute')
		} else {
			steps.css('position', 'fixed')
		}
	})
})

// Initialises and opens the image capture modal
function displaySelfieModal() {

	let actionButtons = $('#selfieActions').find('.ui')

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
							.catch(console.log('>>> Camera not available'))
	}
}

// Captures an image from the camera feed
function captureImage() {

	let snapshot = $('#snapshot')
	let cameraFeed = $('#cameraFeed')
	let actionButtons = $('#selfieActions').find('.ui.button')

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
	$('#uploadInput').addClass('disabled')

	// Build the request data - a list of selected files
	let imageData = new FormData()
	let filesSource = $('#filesSource')

	if (filesSource.text() == 'Disk') {
		// File source is the file input
		const files = $('#fileInput').prop('files')
		for (let i = 0; i < files.length; i++) {
			imageData.append('files-' + (i + 1), files[i])
		}
		uploadFilesAjax(imageData)
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
			uploadFilesAjax(imageData)
		})
	}
}

// Actually performs the AJAX call which saves the files and initialises its channel and FFT images
function uploadFilesAjax(imageData) {

	$.ajax({
		url: '/uploads/inputs',
		method: 'POST',
		data: imageData,
		processData: false,
		contentType: false,
		success: function(data) {
			displayNotification({'text': 'File Upload Succeeded!'})
			
			// Launch the initialisations procedure
			$.ajax({
				url: '/initialisations/',
				method: 'POST',
				data: JSON.stringify({'files': data}),
				contentType: 'application/json',
				success: function(_data) {},
				error: function(_request, _status, _error) {
					console.log('>>> Error during initialisations process')
				}
			})

			// Direct the user to the Operation Selection Step
			$('#fileSelectionContent').css('display', 'none')
			$('#operationSelectionContent').css('display', 'block')
			$('#steps').children('.step').first().removeClass('active')
			$('#steps').children('.step').first().addClass('completed')
			$('#steps').children('.step').eq(1).addClass('active')
			$('#homeButton').css('display', 'inline-block')

			// Populate the container holding uploaded images
			populateFilesAndOperationsContainer(data)

			// Detach any existing click events and attach another one which deletes the inputs and pickles
			$('#homeButton').off('click')
							.click(function() {
								openResetDialog(data['image'], 'PICKLES_INPUTS')
							})
		},
		error: function(_request, _status, _error) {
			displayNotification({'text': 'File Upload failed!', 'type': 'error'})			
			$('#uploadButton').removeClass('disabled')
		}
	})
}
