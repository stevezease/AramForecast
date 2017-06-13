//Use on aram-ranked.info/champions

var jsonData = {};
c = document.getElementsByClassName("row-link");
for(i = 0; i<c.length; i++){
    champion = c[i].getElementsByClassName("summoner")[0].innerText;
    percent = c[i].getElementsByClassName("progress-bar")[0].innerText.replace(/\D/g,'');
	console.log(champion + ": " + percent);
	jsonData[champion] = percent;
}
JSON.stringify(jsonData, 0, 4);