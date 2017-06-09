// This is a function that will be used by spirit/topic/_top_bar.html
// When someone clicks 


function go_to_course_number(url) {
  var no = document.getElementById("course_no").value
  window.open(url + no, '_self', false) 
}
