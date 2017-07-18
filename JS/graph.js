function graph() {
	var min =99999;
	var max = 0; 
	var total = 0; 
	var cdf = 0;
	for(var key in stats){
		if(Number(key)>max)
			max = Number(key);
		if(Number(key)<min)
			min = Number(key);
		total = total + stats[key];

	}
	console.log("total: "+total);
	var c = document.getElementById("myCanvas");
	var ctx = c.getContext("2d");
	ctx.clearRect(0, 0, c.width, c.height);
	var w = c.width;
	c.width = 1;
	c.width = w;
	ctx.lineWidth=1;
	ctx.fillStyle = "gold";
	ctx.strokeStyle="#e2e6e9";
	ctx.font = "8px Arial";
	ctx.fillText(min+"%",0,c.height-2);
	ctx.fillText(max+"%",c.width-22,c.height-2);
	for(var i = min; i <= max; i+=.1){
			i = Math.round(i*10)/10;
			if(i == Number(chance))
			{
				ctx.strokeStyle="#ff2800";
				ctx.beginPath();
				ctx.moveTo((i-min)*16, c.height-13);
				ctx.lineTo((i-min)*16-5, c.height-9);
				ctx.lineTo((i-min)*16+5, c.height-9);
				ctx.fillStyle = "#ff2800";
				ctx.fill();

			}

			if(i < Number(chance)){
				ctx.strokeStyle="#99a6b2";
				if(stats[i.toString()])
				cdf = cdf + stats[i];
			}
			ctx.beginPath();
			ctx.moveTo((i-min)*16, c.height-15);
			ctx.lineTo((i-min)*16,(c.height-Number(stats[i])/23000)-15);
			ctx.stroke();
			ctx.strokeStyle="#374049";
		}
		var percentage = Math.round((cdf/total)*100000)/100000;
		console.log(cdf +"/" + total  + "=" + percentage);
		var tb = document.getElementById("tb");
		var ranking = document.getElementById("ratio");

		if(percentage<.5){

			tb.innerText = "Bottom";
			ranking.innerText = Math.round((percentage)*10000)/100;
		}else{
			tb.innerText = "Top";
			ranking.innerText = Math.round((1-percentage)*10000)/100;
		}
	}
/*
	var s =0; 

	function pulse(c,ctx,min,max){
var interval = setInterval(function() { 
				if(s%2 == 0){
                ctx.strokeStyle="#ff2800";
                ctx.beginPath();
				ctx.moveTo((i-min)*16, c.height-15);
				ctx.lineTo((i-min)*16,(c.height-Number(stats[i])/42000)-15);
				ctx.stroke();
				ctx.beginPath();
				ctx.moveTo((Number(chance)-min)*16, c.height-13);
				ctx.lineTo((Number(chance)-min)*16-5, c.height-9);
				ctx.lineTo((Number(chance)-min)*16+5, c.height-9);
				ctx.fillStyle = "#ff2800";
				ctx.fill();}
				else {
				ctx.strokeStyle="#801300";
                ctx.beginPath();
				ctx.moveTo((i-min)*16, c.height-15);
				ctx.lineTo((i-min)*16,(c.height-Number(stats[i])/42000)-15);
				ctx.stroke();
				ctx.beginPath();
				ctx.moveTo((Number(chance)-min)*16, c.height-13);
				ctx.lineTo((Number(chance)-min)*16-5, c.height-9);
				ctx.lineTo((Number(chance)-min)*16+5, c.height-9);
				ctx.fillStyle = "#801300";
				ctx.fill();
				}
				s++;
      }, 1000);

	}*/