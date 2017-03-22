<?php 
function getdb() {
    $conn_string = "host=dbhost dbname=db user=php_readonly password=passwod";
      $db = pg_connect($conn_string) or die('connection failed');
      return $db;
}

?>
