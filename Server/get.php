

<?php
echo "Für die letzten 14 Tage.<br><br>";
echo "Korrekte Eingaben:<br>";
$row = 1;
if (($handle = fopen("data.csv", "r")) !== FALSE) {
    $last_date = 0;
    $datatowrite_index =0;
    while (($data = fgetcsv($handle, 1000, ",")) !== FALSE) {
        $row++;
        $date_parsed = date_create_from_format("d.m.Y H:i:s", $data[0]);
        $deletionDate = new DateTime('- 14 days', new DateTimeZone('Europe/Vienna'));
        $daysDiff = (int)date_diff($deletionDate, $date_parsed)->format('%R%a');
        if($daysDiff >= 0 ) {
          if(date_format($last_date, 'Y-m-d') != date_format($date_parsed, 'Y-m-d')){
            echo "<b>".date_format($date_parsed, 'Y-m-d').":</b><br>";
          }
          if( $data[2] == "noFile;"){
            echo "&nbsp;&nbsp;".date_format($date_parsed, 'H:i:s').", ".trim($data[1],";")."<br>\n";
          }
          else{
            echo "&nbsp;&nbsp;".date_format($date_parsed, 'H:i:s').", <a href='".trim($data[2],";")."'>".trim($data[1],";")."</a><br>\n";
          }
          $datatowrite[$datatowrite_index] = $data[0].",".$data[1].",".$data[2]."\n";
          $datatowrite_index++;
        }
        else{
          unlink($data[2]);//delete the picture
        }
        $last_date = $date_parsed;
    }
    fclose($handle);
    $writeonly = fopen("data.csv", "w") or die("Unable to open file!");
    for($i=0; $i<=$datatowrite_index; $i++){
      fwrite($writeonly, $datatowrite[$i]);
    }

    fclose($writeonly);
}

echo "<br><br>Inkorrekte Eingaben:<br>";
$row = 1;
if (($handle = fopen("dropouts.csv", "r")) !== FALSE) {
  $last_date = 0;
  $datatowrite_index =0;
  while (($data = fgetcsv($handle, 1000, ",")) !== FALSE) {
      $row++;
      $date_parsed = date_create_from_format("d.m.Y H:i:s", $data[0]);
      $deletionDate = new DateTime('- 14 days', new DateTimeZone('Europe/Vienna'));
      $daysDiff = (int)date_diff($deletionDate, $date_parsed)->format('%R%a');
      if($daysDiff >= 0 ) {
        if(date_format($last_date, 'Y-m-d') != date_format($date_parsed, 'Y-m-d')){
          echo "<b>".date_format($date_parsed, 'Y-m-d').":</b><br>";
        }
        if( $data[2] == "noFile;"){
          echo "&nbsp;&nbsp;".date_format($date_parsed, 'H:i:s').", ".trim($data[1],";")."<br>\n";
        }
        else{
          echo "&nbsp;&nbsp;".date_format($date_parsed, 'H:i:s').", <a href='".trim($data[2],";")."'>".trim($data[1],";")."</a><br>\n";
        }

        $datatowrite2[$datatowrite_index] = $data[0].",".$data[1].",".$data[2]."\n";
        $datatowrite_index++;
      }
      else{
        //unlink($data[2]);
        echo "DELETE:".$data[2];
      }
      $last_date = $date_parsed;
  }
  fclose($handle);
  $writeonly = fopen("dropouts.csv", "w") or die("Unable to open file!");
  for($i=0; $i<=$datatowrite_index; $i++){
    fwrite($writeonly, $datatowrite2[$i]);
  }

  fclose($writeonly);
}
?>
