var unused = "this is never used";

function doStuff(x) {
  if (x == 5) {
    console.log("five");
  }
  var another_unused = 42;
  return x;
}

doStuff(1);
