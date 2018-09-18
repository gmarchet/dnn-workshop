var luisIntent = require('./luis.js');
luisIntent.getLuisIntent('get dental claim for Dr. Jason Tate').then(response =>{
console.log('Topring Intent--- '+response);
});