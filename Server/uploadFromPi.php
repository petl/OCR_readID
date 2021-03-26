<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html><head>
<meta name="description" content="Anwesenheitsliste">
<meta name="author" content="peter@traunmueller.net">
  <link href="style.css" rel="stylesheet" type="text/css">
  <meta charset="UTF-8">
  <title>Anwesenheitsliste</title>
<meta name=viewport content="width=device-width, initial-scale=1, user-scalable=yes">
</head>

<body>
<form name="form1" action="./uploadFromPi.php" method="post" enctype="multipart/form-data">
Deine Matrikelnummer: <br>
  <input name="MatrNr" placeholder="0123456" type="text" size=8>  <br>
  <input type="file" name="fileToUpload" id="fileToUpload" accept=".jpg"><br>
  <input value="Eintragen" type="submit"><br>
</form><br>

<?php
$MatrNr_Input= $_POST["MatrNr"];
var_dump($_REQUEST);

$target_file = "../daten/pictures/" . basename($_FILES["fileToUpload"]["name"]);
if($MatrNr_Input != ""){
  if(is_numeric($MatrNr_Input) && (strlen((string)$MatrNr_Input)>=7) && (strlen((string)$MatrNr_Input)<=8)){

    if (move_uploaded_file($_FILES["fileToUpload"]["tmp_name"], $target_file)) {
      echo "The file ". htmlspecialchars( basename( $_FILES["fileToUpload"]["name"])). " has been uploaded.<br>";
    } else {
      echo "Sorry, there was an error uploading your file.";
    }


    $filename = "data.csv";
    $myfile = fopen("../daten/".$filename, "a+") or die("Unable to open file!");
    fwrite($myfile, date("d.m.Y H:i:s").",".$MatrNr_Input.",".$target_file.";\n");
    fclose($myfile);
    echo "<font color='green'>Danke!<br>";
    echo "Deine Matrikelnummer wurde für den ".date("d.m.Y")." gepeichert.<br><br></font>";
  }
  else{
    $filename = "dropouts.csv";
    $myfile = fopen("../daten/".$filename, "a+") or die("Unable to open file!");
    fwrite($myfile, date("d.m.Y H:i:s").",".$MatrNr_Input.",".$target_file.";\n");
    fclose($myfile);
    echo "<font color='red'>Matrikelnummer nicht erkannt. <br> Bitte erneut eingeben!<br><br></font> ";
  }
}
else{
  echo "<br><br><br>";
}

?>



<br>
<a href="https://www.quiescentcurrent.com">Kontakt</a> <br>peter@traunmueller.net - 2020

</div>

</body></html>
