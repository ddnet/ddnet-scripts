<html>
<?php if(isset($_SERVER['PHP_AUTH_USER'])) {
	$auths = fopen("ddrace_auths.cfg", "r");
	if(!$auths) {
		exit;
	}

	$hash = null;
	$salt = null;
	while(!feof($auths)) {
		$line = fgets($auths);
		if($line[0] == '#') {
			continue;
		}

		$tokens = explode(" ", $line);
		if($tokens[0] !== "auth_add_p") {
			continue;
		}

		if($tokens[1] === $_SERVER['PHP_AUTH_USER']) {
			$hash = $tokens[3];
			$salt = $tokens[4];
			break;
		}
	}

	if(!$hash)
	{
		header('WWW-Authenticate: Basic realm="teehistorian"');
		header('HTTP/1.0 401 Unauthorized');
		echo "401 Unauthorized";
		exit;
	}

	$ctx = hash_init("md5");
	hash_update($ctx, $_SERVER['PHP_AUTH_PW']);
	hash_update($ctx, hex2bin($salt));

	if($hash !== hash_final($ctx))
	{
		header('WWW-Authenticate: Basic realm="teehistorian"');
		header('HTTP/1.0 401 Unauthorized');
		echo "401 Unauthorized";
		exit;
	}
?>
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
<tr><th>Index file</th><th>File size</th><th>Transfer size</th><th>Last modified</th></tr>
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
        echo '<tr><td><a href="' . $path . '">' . $path . '</a></td><td style="text-align: right;">' . formatMiB($size) . '</td><td style="text-align: right;">' . formatMiB($sizeCompressed) . '</td><td>' . date("Y-m-d H:i", filemtime($path)) . '</td></tr>';
      }
    }
  }
}
?>
</table>
<p>Execution time: <?php echo number_format((microtime(true) - $_SERVER["REQUEST_TIME_FLOAT"]) * 1000, 1); ?> ms</p>
<?php } else {
	header('WWW-Authenticate: Basic realm="teehistorian"');
	header('HTTP/1.0 401 Unauthorized');
	echo "401 Unauthorized";
	exit;
}?>
</html>
