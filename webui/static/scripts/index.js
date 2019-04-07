"use strict";

let imageCapture // Reference used for capturing images

// Attach handlers on document ready
$(document).ready(function() {
	let fileInput = $('#fileInput')
	let uploadButton = $('#uploadInput')

	// Display relevant information depending on the number of selected files
	$(fileInput).change(function(event) {
		let countParagraph = $('#filesCount')
		let fileNames = $('#fileNames')
		let filesContainer = $('#filesContainer')
		let filesCount = event.target.files.length

		// Remove existing file names and images, if user reselects files
		$(fileNames).empty()
		$(filesContainer).empty()

		if (filesCount != 0) {
			$(uploadButton).removeClass('disabled')
			$(countParagraph).html('Files Loaded: ' + filesCount) // TODO - Style this to be civilised

			for (let i = 0; i < filesCount; i++) {
				let fileName = $('<span>').text(event.target.files[i]['name'] + ' ') // TODO - Change to tags
				$(fileNames).append(fileName)

				let imageElement = $('<img>')
				$(imageElement).prop('src', URL.createObjectURL(event.target.files[i]))
				$(imageElement).prop('alt', 'Image Preview not Available')
				$(imageElement).prop('height', '200')

				$(filesContainer).append($('<div>').append(imageElement))
			}
		} else {
			$(uploadButton).addClass('disabled')
			$(countParagraph).html('No Files loaded yet')
		}
	})
})

// Initialises and opens the image capture modal
function openSelfieModal() {
	$('#selfieModal').modal({
							onHide: function() {
								if (imageCapture.track.readyState != 'ended') {
									imageCapture.track.stop()
								}
								console.log('MODAL HIDDEN')
							},
							onApprove: function() {
								console.log('>>> Modal SUBMIT Button Pressed')
							},
							onDeny: function() {
								console.log('>>> Modal CANCEL Button Pressed')
							}
						}).modal('show')

	// Initialise the camera feed if necessary
	if (imageCapture === undefined || imageCapture.track.readyState == 'ended') {
		navigator.mediaDevices.getUserMedia({video: true})
							.then(mediaStream => {
								document.querySelector('video').srcObject = mediaStream;
								const track = mediaStream.getVideoTracks()[0]
								imageCapture = new ImageCapture(track)
							})
	}
}

// Captures an image from the camera feed
function captureImage() {
	let snapshot = $('#snapshot')
	let cameraFeed = $('#cameraFeed')

	if (snapshot.css('display') == 'none') {
		// Capture image and display it
		imageCapture.takePhoto()
					.then(blob => {
						snapshot.prop('src', URL.createObjectURL(blob))
						snapshot.toggle()
						cameraFeed.toggle()
					})
	} else {
		// Redisplay the video feed
		snapshot.css('display', 'none')
		cameraFeed.toggle()
	}
}

// Makes a POST request, uploading the selected files to the server
// Upon completion of the upload, the server sends the URLs of the files and the function displays
// those files
function uploadFiles() {
	// Disable the upload button, while the upload is being performed
	let uploadButton = $('#uploadInput')
	$(uploadButton).addClass('disabled')

	// Build the request data - a list of uploaded files
	const files = $('#fileInput').prop('files')
	let imageData = new FormData()
	for (let i = 0; i < files.length; i++) {
		imageData.append('files-' + (i + 1), files[i])
	}

	// Perform the actual server call which saves the files
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
			
			// Enable the upload button back
			$(uploadButton).removeClass('disabled')
			
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
			$(uploadButton).removeClass('disabled')
		}
	})
}

// This function switches the application mode between 'Image' and 'Video'
// TODO - Change the page content accordingly (<title>, <h1> title and other stuff)
function changeMode() {

	let visibleContent = $('#switchMode').find('.visible').first()
	let hiddenContentIcon = $('#switchMode').find('.hidden').first().find('.icon').first()

	if ($(visibleContent).html().includes('VIDEO')) {
		$(visibleContent).html('SWITCH TO IMAGE MODE')
	} else {
		$(visibleContent).html('SWITCH TO VIDEO MODE')
	}

	$(hiddenContentIcon).toggleClass('image')
	$(hiddenContentIcon).toggleClass('video')
}
