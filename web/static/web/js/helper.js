/**
 * Created by vikrant on 20/2/17.
 *
 var prime = 16777213;
 var colorValue = (location[3]).toString().hashCode()%prime;
 console.log(colorValue)
 */
String.prototype.hashCode = function() {
  var hash = 0, i, chr, len;
  if (this.length === 0) return hash;
  for (i = 0, len = this.length; i < len; i++) {
    chr   = this.charCodeAt(i);
    hash  = ((hash << 5) - hash) + chr;
    hash |= 0; // Convert to 32bit integer
  }
  return hash;
};
function getRandomInt(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

function getDirectionText(bearing) {
    var dir = Math.floor((bearing+22.5)/45) % 8;
    switch (dir) {
        case 0: return "N";
        case 1: return "NE";
        case 2: return "E";
        case 3: return "SE";
        case 4: return "S";
        case 5: return "SW";
        case 6: return "W";
        case 7: return "NW";
    }
    return "";
}