<?php

// note: this generic function has been hacked to demo
// the software database backend code. In particular,
// the 2nd field should be the pkg name so a link will
// be correctly generated.
function print_table($result, $show_headers = True) {
  echo "<table border=\"1\">\n";
  $n = mysql_num_fields($result);

  if($show_headers) {
    echo "<tr>\n";
    for($i = 0; $i < $n; $i++) {
      echo "<td>";
      echo mysql_field_name($result, $i);
      echo "</td>\n";
    }
    echo "</tr>\n";
  }

  while($row = mysql_fetch_row($result)) {
    echo "<tr>\n";
    for($j = 0; $j < $n; $j++) {
      echo "<td>";
      // hack to make the pkg name a link
      if($j == 1) {
        echo "<a href='/?pkg=$row[$j]'>$row[$j]</a>";
      } else {
        echo $row[$j];
      }
      echo "</td>\n";
    }
    echo "</tr>\n";
  }

  echo "</table>\n";
}

?>
