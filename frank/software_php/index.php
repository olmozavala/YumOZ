<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
"http://www.w3.org/TR/html4/loose.dtd">
<html>
  <head>
    <title>Software DB Demo</title>
    </head>
  <body>
    <?php
    require_once 'print_table.php';
    $con = mysql_connect("localhost","root"); //,"abc123");
    if (!$con) {
      die('Could not connect: ' . mysql_error());
    }

    if(empty($_GET['pkg'])) {
      // Let's show the package list
      echo "<center><h1>Packages</h1></center>\n";
      echo "\n<center><a href='/'>Home</a></center>\n";
      mysql_select_db("ac_software", $con);
      $sql = "SELECT `id`,`name`,`version`,`release` FROM ac_softwareitem";
      $result = mysql_query($sql, $con);
      if(!$result) {
        mysql_close($con);
        die('Error running query: ' . mysql_error());
      }
      print_table($result);
    } else {
      // Print information about a single package, include dep info
      $pkg = $_GET['pkg'];

      // Print a row with teh package info
      $sql = "SELECT `id`,`name`,`version`,`release`,`summary`,`description` FROM ac_softwareitem WHERE `name`='$pkg'";
      $result = mysql_query($sql, $con);
      if(!$result) {
        mysql_close($con);
        die('Error running query: ' . mysql_error());
      }
      echo "<center><h1>Package $pkg</h1></center>\n";
      echo "\n<center><a href='/'>Home</a></center>\n";
      print_table($result);

      // Reset the result, get the id of the pkg
      mysql_data_seek($result,0);
      $row = mysql_fetch_array($result);
      $id = $row['id'];

      // Get the dep info for the package
      $sql = "SELECT * FROM ac_softwaredepen WHERE `id_software`='$id'";
      $result = mysql_query($sql, $con);
      if(!$result) {
        mysql_close($con);
        die('Error running query: ' . mysql_error());
      }

      // for each dep, get and print package info
      while($row = mysql_fetch_row($result)) {
        $dep_id = $row['id_dependen'];
        $dep_sql = "SELECT `id`,`name`,`version`,`release` FROM ac_softwareitem WHERE `id_software`='$dep_id'";
        $dep_result = mysql_query($dep_sql, $con);
        if(!$dep_result) {
          mysql_close($con);
          die('Error running query: ' . mysql_error());
        }
        print_table($dep_result, False);
      } 
    }

    echo "\n<center><a href='/'>Home</a></center>\n";
    mysql_close($con);
    ?>
  </body>
</html>
