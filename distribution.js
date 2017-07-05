var iter = 0;
var arr = []; 
var string = []; 
var ans = {};
for(var key in percent){
	arr.push(key);

}

function combination(array,len,start,resultstring){
	if(len == 0){
		iter++;
		var result = 0;
		for(var i =0; i<resultstring.length; i++){
result = Number(result) + Number(percent[resultstring[i]]);
		}
		result = Math.round((result/5)*1000)/1000; 
		if(ans[result] == undefined)
			ans[result] = 1;
		else {
			ans[result] = ans[result] +1; 
		}
	return;
	}
for(var i = start; i<=(arr.length-len);i++){
	resultstring[5-len] = arr[i];
	combination(arr,(len-1),(i+1),resultstring);
}
return;
}
combination(arr,5,0,string);


