let table; 
let current_frame = 0;
let scrubbing = 1;
let DISTANCE_SCALE = 2e+9;
let WIDTH = 800;
let HEIGHT = 800;
let MINIWIDTH = 500;
let MINIHEIGHT = 400;

let eclipse_num = 0;
let prev_frame_eclipse = false;

let DATA;
let GRAPH_TEMPLATE;

let CELESTIAL_BODY_DICT = {
  "Earth": {"Render_Diameter": 5, "Orbital_Radius": 1.496e+11, "colour": [100, 255, 255]},
  "Jupiter": {"Render_Diameter": 10, "Orbital_Radius": 7.785e+11, "colour": [255, 180, 180]},
  "Io": {"Render_Diameter": 2, "Orbital_Radius": 4.217e+8, "colour": [255, 255, 255]},
  "Sun": {"Render_Diameter": 50}
};

function get_Row(current_frame) {
  return table.getRow(current_frame);
}

function render_Sun() {
  noStroke();
  fill(255, 255, 255);
  
  render_diameter = CELESTIAL_BODY_DICT.Sun.Render_Diameter;
  
  circle(HEIGHT / 2, WIDTH / 2, render_diameter); //Sun
  
  fill(0, 0, 0, 0);
  stroke(255, 255, 255);
  rect(0, 0, 800, 800); //Frame
}

function render_planet(Planet, current_frame) {
  X = get_Row(current_frame).get(Planet + "_X");
  Y = get_Row(current_frame).get(Planet + "_Y");
  
  scaled_X = X / DISTANCE_SCALE + WIDTH / 2;
  scaled_Y = -Y / DISTANCE_SCALE + HEIGHT / 2;
  
  render_diameter = CELESTIAL_BODY_DICT[Planet].Render_Diameter;
  orbital_radius = CELESTIAL_BODY_DICT[Planet].Orbital_Radius;
  colour = CELESTIAL_BODY_DICT[Planet].colour;
  
  if (Planet == "Earth") {
    stroke(0, 255, 0);
  } else{
    stroke(255, 0, 0);
  }
  line(WIDTH/2, HEIGHT/2, scaled_X, scaled_Y)
  
  // Orbit
  noFill();
  stroke(255, 255, 255, 100);
  circle(WIDTH/2, HEIGHT/2, 2 * orbital_radius / DISTANCE_SCALE);
  
  // Planet
  fill(colour[0], colour[1], colour[2]);
  noStroke();
  circle(scaled_X, scaled_Y, render_diameter);
}

function render_eclipse(current_frame) {  
  if (get_Row(current_frame).get("Eclipse_observed") != "") {
    if (!prev_frame_eclipse) {
      prev_frame_eclipse = true;
      eclipse_num += 1
    }
    
    Io_X = get_Row(current_frame).get("Io_X");
    Io_Y = get_Row(current_frame).get("Io_Y");

    X = get_Row(current_frame).get("Eclipse_Observation_Origin_X");
    Y = get_Row(current_frame).get("Eclipse_Observation_Origin_Y");
    r = get_Row(current_frame).get("Eclipse_Observation_Light_Front_Radius");  
    
    scaled_X = X / DISTANCE_SCALE + WIDTH / 2;
    scaled_Y = -Y / DISTANCE_SCALE + HEIGHT / 2;
    scaled_r = r / DISTANCE_SCALE;
    stroke(255, 255, 100, 255);
    fill(255, 255, 100, 100);
    
    if (scrubbing > 5) { // Some rendering trickery here because c is too god damn fast
      
      Earth_X = get_Row(current_frame).get("Earth_X");
      Earth_Y = get_Row(current_frame).get("Earth_Y");
      
      Earth_dist = sqrt(sq(Earth_X - X) + sq(Earth_Y - Y));
      Earth_render_dist = Earth_dist / DISTANCE_SCALE;
      
      scaled_r = max(Earth_render_dist * 49/50 + random() * Earth_render_dist * 2/50, scaled_r)
    }
  
    circle(scaled_X, scaled_Y, 2*scaled_r);
    
  }
  else{
    prev_frame_eclipse = false;
  }
}


function secondsToDhms(seconds) {
  seconds = Number(seconds);
  var d = Math.floor(seconds / (3600*24));
  var h = Math.floor(seconds % (3600*24) / 3600);
  var m = Math.floor(seconds % 3600 / 60);
  var s = Math.floor(seconds % 60);

  var dDisplay = d > 0 ? d + (d == 1 ? " day, " : " days, ") : "";
  var hDisplay = h >= 0 ? h + (h == 1 ? " hour, " : " hours, ") : "";
  var mDisplay = m >= 0 ? m + (m == 1 ? " minute, " : " minutes, ") : "";
  var sDisplay = s >= 0 ? s + (s == 1 ? " second" : " seconds") : "";
  return dDisplay + hDisplay + mDisplay;
}

function render_time(current_frame) {
  time = get_Row(current_frame).get(0);
  fill(255, 255, 255);
  noStroke(255, 255, 255);
  
  if (get_Row(current_frame).get("Eclipse_observed") != "") {
    stroke(255, 255, 100, 255);
    fill(255, 255, 100, 100);
    
  }
  
  text(secondsToDhms(time), 10, 30);
  text("Eclipse Number: " + eclipse_num, 10, 60);
}

function render_mini_frame(current_frame) {
  stroke(255, 255, 255);
  fill(0, 0, 0, 255); 
  rect(WIDTH, HEIGHT-MINIHEIGHT, MINIWIDTH, MINIHEIGHT); // Mini frame
  
  if (get_Row(current_frame).get("Eclipse_observed") != "") {
    fill(255, 255, 100, 100);
    rect(WIDTH, HEIGHT-MINIHEIGHT, MINIWIDTH, MINIHEIGHT); // Mini frame
  } 
  
  MiniCentreX = WIDTH+MINIWIDTH / 2;
  MiniCentreY = HEIGHT-MINIHEIGHT / 2;
  
  MiniScale = 2.5e+6;
  
  Jupiter_Radius = 7.149e+7;
  IO_RADIUS = 1.822e+6;
  IO_ORBITAL_RADIUS = 4.217e+8;
  
  fill(255, 255, 255, 100);
  rect(MiniCentreX, MiniCentreY - Jupiter_Radius / MiniScale, 250, 2 * Jupiter_Radius / MiniScale); //Jupiter Shadow
  
  noStroke();
  fill(255, 180, 180);
  circle(MiniCentreX, MiniCentreY, Jupiter_Radius * 2 / MiniScale); //Jupiter
  
  noFill();
  stroke(255, 255, 255, 100);

  circle(MiniCentreX, MiniCentreY, IO_ORBITAL_RADIUS * 2 / MiniScale); // Io Orbit
  
  Io_X = get_Row(current_frame).get("Io_X") - get_Row(current_frame).get("Jupiter_X");
  Io_Y = get_Row(current_frame).get("Io_Y") - get_Row(current_frame).get("Jupiter_Y");
  
  fill(255, 255, 255);
  circle(MiniCentreX + Io_X / MiniScale, MiniCentreY - Io_Y / MiniScale, 2 * IO_RADIUS / MiniScale); // Io
}

function render_graph(eclipse_num) {

  fill(0, 0, 0);
  stroke(255, 255, 255);
  rect(WIDTH, 0, MINIWIDTH, HEIGHT-MINIHEIGHT);
  
  GRAPH_TEMPLATE.resize(MINIWIDTH, MINIHEIGHT);
  image(GRAPH_TEMPLATE, WIDTH, 0);
  
  for (var i = 0; i < eclipse_num; i++) {
    period = DATA[i] / 3600;
    fill(0, 100, 255);
    noStroke();
    circle(WIDTH * 1.1 + i * 1.58, (HEIGHT-MINIHEIGHT) / 2 - (period - 42.51719) * 35500, 3);
  }
  
}

function preload() {
  table = loadTable('https://docs.google.com/spreadsheets/d/e/2PACX-1vTgx1xu3f2La3t03gbxOkV5ndUooPOGTZ1gl7vlQqVuX3XntBQI0beR4E_HHfNG0ssUMNQ4fDveI6UF/pub?gid=1285170362&single=true&output=csv', 'csv', 'header')
  DATA = loadJSON('data.json');
  GRAPH_TEMPLATE = loadImage('Io Periods blank.png');
}

function change_speed() {
  if (scrubbing == 1) {
    scrubbing = 18;
  }
  else{
    scrubbing = 1;
  }
}

function setup() {
  createCanvas(WIDTH+500, HEIGHT);
  frameRate(50);
  
  speedBtn = createButton('Change Rendering Speed');
  speedBtn.position(0, 50);
  speedBtn.mousePressed(change_speed); 
}

function draw() {
  background(0);

  render_planet("Jupiter", current_frame);
  render_planet("Earth", current_frame);
  
  render_Sun();
  render_eclipse(current_frame);
  
  render_time(current_frame);
  
  render_mini_frame(current_frame);
  render_graph(eclipse_num);

  if (current_frame < 288570) {
    current_frame += scrubbing;
  }
  else {
    current_frame = 288570
  }
}