<html>
<form action="">ID: <input type="text" name="id"><input type="submit" value="Search"></form>
<?php
function main() {
  if (!isset($_GET['id'])) {
    return;
  }

  if (!preg_match('/^[0-9a-fA-F\-]+$/', $_GET['id'])) {
    echo "invalid ?id parameter passed";
    return;
  }

  $dirs = new DirectoryIterator("data");
  foreach ($dirs as $dir) {
    if ($dir->isDot()) {
      continue;
    }
    $paths = [
      "data/" . $dir . "/" . $_GET['id'] . ".teehistorian",
      "data/" . $dir . "/" . $_GET['id'] . ".teehistorian.xz"];
    foreach ($paths as $path) {
      if (file_exists($path)) {
        echo "<a href=\"" . $path . "\">" . $path . "</a>";
        return;
      }
    }
  }
  echo $_GET['id'] . " not found";
}
main();
?>
<br>
<?php echo 'Execution time: ' . number_format((microtime(true) - $_SERVER["REQUEST_TIME_FLOAT"]) * 1000, 1) . " ms";?>
</html>
