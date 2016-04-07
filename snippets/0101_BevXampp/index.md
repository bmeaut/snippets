---
layout: default
codename: BevXampp
title: Bevezetés az XAMPP használatába
tags: info2
authors: Csorba Kristóf
---

# XAMPP - PHP - MySQL - phpMyAdmin

A következőkben készítünk egy olyan PHP alapú weboldalt, mely egy MySQL adatbázis segítségével el tud menteni időpont-hőmérséklet párokat, valamint meg tudja őket jeleníteni.

Amennyiben a gépünkön a 80-as porton fut a webszerver, az alábbi URL "megnyitásával" tudunk majd új adatot felvenni. (Ez elég egyszerű ahhoz, hogy egy mikrovezérlő is könnyen meg tudja hívni.)

    http://localhost/add.php?time=201506020845&t=24

Először is kell egy adatbázis, benne az alábbi táblával. (Most a timestamp formátummal az egyszerűség kedvéért nem foglalkozunk, sima stringként mentjük el.)

    create table Measurement (
      MeasurementID int primary key auto_increment,
      Timestamp char(12),
      Temperature float
    );

Kell egy add.php:

    <html>
    <head><title>Add</title></head>
    <body>
    <?php
        if( isset( $_GET['time'] ) ) {
            $time = $_GET['time'];
            $t = $_GET['t'];
            $mysqli = new mysqli("localhost","root","","measurements");
            if($mysqli->connect_errno)
            {
               echo "error: " . $mysqli->connect_error . "<BR/>";
            }

            $query=sprintf("INSERT INTO Measurement(Timestamp, Temperature) VALUES('%s',%s)"
               , mysql_real_escape_string($time)
               , mysql_real_escape_string($t) );
            $mysqli->query($query);
            $mysqli->close();
            echo('Done');
        }
    ?>
    </body>
    </html>

Ezen kívül kelleni fog egy megjelenítő oldal:

    <html>
    <head><title>Mérési eredmények</title></head>
    <body>
    <H1>Az eddigi mérési eredmények:</H1>
    <TABLE border="1">
    <TR><TD>Időpont</TD><TD>Hőmérséklet</TD></TR>
    <?php
      $mysqli = new mysqli("localhost", "root", "", "measurements");
      if ($mysqli->connect_errno) {
        echo "<P/>Failed to connect to MySQL: (" . $mysqli->connect_errno . ") " . $mysqli->connect_error;
      }
      else
      {
        $mysqli->real_query("SELECT Timestamp,Temperature FROM Measurement");
        $result = $mysqli->use_result();
        while ($row = $result->fetch_row()) {
          printf("<TR><TD>%s</TD><TD>%s</TD></TR>\n", $row[0], $row[1]);
        }
        $result->close();
        $mysqli->close();
      }
    ?>
    </TABLE>
    </body>
    </html>

TODO: létrehozás, telepítés, futtatás

<small>Szerzők, verziók: Csorba Kristóf</small>
