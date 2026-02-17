<?php
function greet( string $name , int $age)
{
  if( $age>0 ){
    return "Hello, " . $name . "! Age: ".$age ;
  }
    return NULL;
}
