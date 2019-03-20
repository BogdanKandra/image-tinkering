// Attach handlers on document ready
$(document).ready(function() {

	let imgElement = $('#imagesrc')
	let fileInput = $('#fileInput')
	let uploadButton = $('#uploadInput')

	// Disable the upload button if no file is selected, enable it otherwise
	$(fileInput).change(function(event) {
		if (event.target.files.length != 0) {
			$(imgElement).prop('src', URL.createObjectURL(event.target.files[0]))
			$(uploadButton).prop('disabled', false)
		} else {
			$(uploadButton).prop('disabled', true)
		}
	})
})

// Makes a POST request, uploading the selected files to the server
// Upon completion of the upload, the server sends the URLs of the files and the function displays
// those files
function uploadFiles() {
	// Disable the upload button, while the upload is being performed
	let uploadButton = $('#uploadInput')
	$(uploadButton).prop('disabled', true)

	// Build the request data - a list of uploaded files
	const files = $('#fileInput').prop('files')
	let imageData = new FormData()
	for (let i = 0; i < files.length; i++)
		imageData.append('files-' + (i + 1), files[i])

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
			
			console.log('>>> ', data)
			
			// Enable the upload button back
			$(uploadButton).prop('disabled', false)
			
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
			$(uploadButton).prop('disabled', false)
		}
	})
}