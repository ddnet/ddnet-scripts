<?php
$error = null;
function getFile($id)
{
	$dirs = new DirectoryIterator("data");
	foreach($dirs as $dir) {
		if($dir->isDot())
			continue;

		$paths = ["data/$dir/$id.teehistorian", "data/$dir/$id.teehistorian.xz"];
		foreach($paths as $path) {
			if(file_exists($path))
				return $path;
		}
	}
	return null;
}

$type = "html";
if($_SERVER['HTTP_ACCEPT'] === "application/json")
	$type = "json";

$file = null;
if(!empty($_GET['id'])) {
	if(!preg_match('/^[0-9a-fA-F\-]+$/', $_GET['id']))
		$error = "invalid ?id parameter passed";
	else
		$file = getFile($_GET['id']);
}

if($type === "html") { ?>
    <html>
    <form action="">ID: <input type="text" name="id"><input type="submit" value="Search"></form>
	<?php
	if($error)
		echo "Error: $error";
    else if($file)
		echo "<a href='$file'>$file</a>";
	?>
    <br>
    <table>
        <thead>
        <tr>
            <th>Index file</th>
            <th>File size</th>
            <th>Transfer size</th>
            <th>Last modified</th>
        </tr>
        </thead>
        <tbody>
		<?php
		function formatMiB($size)
		{
			return number_format($size / 1024 / 1024, 2) . ' MiB';
		}

		foreach(scandir("data") as $dir) {
			if($dir[0] == '.')
				continue;

			$paths = ["data/$dir/index.txt", "data/$dir/index.new.txt"];
			foreach($paths as $path) {
				if(file_exists($path)) {
					$size = filesize($path);
					$sizeCompressed = filesize($path . ".gz");
					if($size > 0) {
						echo '<tr>';
						echo "<td><a href='$path'>$path</a></td>";
						echo "<td style='text-align: right;'>{formatMiB($size)}</td>";
						echo "<td style='text-align: right;'>{formatMiB($sizeCompressed)}</td>";
						echo "<td style='text-align: right;'>" . date('Y-m-d H:i', filemtime($path)) . "</td>";
						echo '</tr>';
					}
				}
			}
		}
		?>
        </tbody>
    </table>
    <p>Execution time: <?php echo number_format((microtime(true) - $_SERVER["REQUEST_TIME_FLOAT"]) * 1000, 1); ?> ms</p>
    </html>

<?php }
else {
	if($type == 'json') {
		header("Content-Type: application/json");
		if($error) {
			http_response_code(400);
			die(json_encode(['error' => $error]));
		}

		if(!$file) {
			http_response_code(404);
			die(json_encode(['error' => "id not found"]));
		}

		http_response_code(200);
		$uri = (!empty($_SERVER['HTTPS']) ? 'https' : 'http') . "://${_SERVER['HTTP_HOST']}${_SERVER['PHP_SELF']}";
		$uri = dirname($uri) . "/" . $file;
		echo json_encode(['url' => $uri]);
	}
}
?>
