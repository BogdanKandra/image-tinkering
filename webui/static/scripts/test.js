$(document).ready(function() {
	console.log('In script')
	let imgElement = $('#imagesrc')
	let inputElement = $('#fileInput')
	$(inputElement).change(function(event) {
		console.log('File was loaded')
		$(imgElement).attr('src', URL.createObjectURL(event.target.files[0]))
	})
})