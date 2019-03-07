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
        echo '<a href="' . $path . '">' . $path . '</a>';
        return;
      }
    }
  }
  echo $_GET['id'] . " not found";
}
main();
?>
<br>
<table>
<tr><th>Index file</th><th>File size</th><th>Transfer size</th></tr>
<?php
function formatMiB($size) {
  return number_format($size / 1024 / 1024, 2) . ' MiB';
}

foreach (scandir("data") as $dir) {
  if ($dir[0] == '.') {
    continue;
  }
  $paths = [
    "data/" . $dir . "/" . "index.txt",
    "data/" . $dir . "/" . "index.new.txt"];
  foreach ($paths as $path) {
    if (file_exists($path)) {
      $size = filesize($path);
      $sizeCompressed = filesize($path . ".gz");
      if ($size > 0) {
        echo '<tr><td><a href="' . $path . '">' . $path . '</a></td><td style="text-align: right;">' . formatMiB($size) . '</td><td style="text-align: right;">' . formatMiB($sizeCompressed) . '</td></tr>';
      }
    }
  }
}
?>
</table>
<p>Execution time: <?php echo number_format((microtime(true) - $_SERVER["REQUEST_TIME_FLOAT"]) * 1000, 1); ?> ms</p>
</html>
