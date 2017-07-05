function cleared() {
	var tags = document.getElementsByClassName("tags");
    for(var i = 0; i< tags.length; i++){
        tags[i].readOnly= false; 
        tags[i].value= ''; 
        tags[i].style.backgroundImage = "none";
        tags[i].placeholder = "Enter Champion Name";
    }
   document.getElementById("eval").innerText = "Evaluate";
   $("#results").slideUp("slow");
   $("#heading").slideDown("slow");

defaultc();

}