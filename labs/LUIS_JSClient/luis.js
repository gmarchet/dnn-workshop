var request = require('request');
var querystring = require('querystring');
 module.exports = {
getLuisIntent:(utterance) => {
 return new Promise((resolve, reject) => { 
   var endpoint = "https://westus.api.cognitive.microsoft.com/luis/v2.0/apps/";
       var luisAppId = "9a233989-f08c-47b1-938a-9f99e439085a";
    var queryParams = {  
           "subscription-key": "a427575d4b224479820f149bf74240e5",      
           "timezoneOffset": "0",     
           "verbose":  true,        
           "q": utterance    }
    var luisRequest =  endpoint + luisAppId +        '?' + querystring.stringify(queryParams);
    request(luisRequest,function (err,response, body) {
            if (err){console.log(err);
               reject(err);
             }else {
                var data = JSON.parse(body);
                    console.log(`Query: ${data.query}`);
                    console.log(`Top Intent: ${data.topScoringIntent.intent}`);
                    console.log('Intents:'); 
                    console.log(data.intents); 
                    var topIntent = data.topScoringIntent.intent;
                    resolve(topIntent);
                  
            }    
    }); 
}); 
}
};
