

<!DOCTYPE html>
<html>

<head>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" integrity="sha384-JcKb8q3iqJ61gNV9KGb8thSsNjpSL0n8PARn9HuZOnIxN0hoP+VmmDGMN5t9UJ0Z" crossorigin="anonymous">
    <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js" integrity="sha384-DfXdz2htPH0lsSSs5nCTpuj/zy4C+OGpamoFVy38MVBnE+IbbVYUew+OrCXaRkfj" crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/popper.js@1.16.1/dist/umd/popper.min.js" integrity="sha384-9/reFTGAW83EW2RDu2S0VKaIzap3H66lZH81PoYlFhbGU+6BZp6G7niu735Sk7lN" crossorigin="anonymous"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js" integrity="sha384-B4gt1jrGC7Jh4AgTPSdUtOBvfO8shuf57BaghqFfPlYxofvL8/KUEfYiJOMMV+rV" crossorigin="anonymous"></script>
    <link rel="stylesheet" href="last.css">
</head>

<body>

<div>
<?php
$servername = "localhost";
$username = "root";
$password = "1234";
$w = $_GET['t'];
$data = "jayanth";

try {
$conn = new PDO("mysql:host=$servername;dbname=$data", $username, $password);
$conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

$s = $conn->query("SELECT * from sample_words where word_name = '$w'");
foreach ($s as $row ) {
    $wid = $row['word_id'] ;
    echo "<h1>". $row['word_name'] . "</h1>";
    echo '<img src="data:image/jpg;charset=utf8;base64,' .base64_encode($row['image']) .'"style="width:300px;"/>' . "<br>";
    echo "Scientific Name: (" . $row['scientific_name']. ")". "<br>";
    echo "Pronunciation: (" . $row['pronunciation']. ")". "<br>";
    echo "-----------------------------"."<br>"."<br>";
    
         $s = $conn->query("SELECT * from synonyms where word_id = $wid");
         foreach ($s as $row ) {
              $sid = $row['synonym_id'];
              echo "<hr>"."Meaning: ".$row['definition'] ."<br>";
              echo "Example: ". $row['example'] . "<br>";
              echo "Synonym: ". $row['synonym_word']. "<br>";
              $s = $conn->query("SELECT * from antonyms where synonym_id = $sid AND word_id = $wid");
              foreach ($s as $row ) {
                echo "Antonym: ". $row['antonym_word'] . "<br>";
                echo "Example: ". $row['example'] . "<br>". "<br>";
              }
             // $s = $conn->query("SELECT * from pos where pos_id = $wid");
             // foreach ($s as $row ) {
                   
                  
               //    echo "Example: ". $row['pos_name'] . "<br>";
                   
             // }
         }
        
         echo "<h2>"."In Other lauguages"."</h2>";
         $s = $conn->query("SELECT * from languages where word_id = $wid");
         echo "<hr>"."HINDI: ";
         foreach ($s as $row ) {
            echo $row['Hindi'] ." ,";
         }
         echo "<br>"."<hr>";
         $s = $conn->query("SELECT * from languages where word_id = $wid");
         echo "SANSKRIT: ";
         foreach ($s as $row ) {
            echo $row['Sanskrit']." ,";
         }
         echo "<br>"."<hr>";

         $s = $conn->query("SELECT * from languages where word_id = $wid");
         echo "TELUGU: ";
         foreach ($s as $row ) {
            echo $row['Telugu']." ,";
         }
         echo "<br>"."<hr>";
             
   }

} catch(PDOException $e) {
echo "Connection failed: " . $e->getMessage();
}
?>
</div>
</body>

</html>



