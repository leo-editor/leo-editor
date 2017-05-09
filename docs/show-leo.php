<?php
//phpinfo();
// Load Leo file 
$leo_file_name = $_FILES['Filedata']['tmp_name'];
// There can be up to 1000 leo files open at a time.
// First, age out any files older than 8 hours
$leo_name_format = "show-leo-%04d.leo"; 
$out_file_name   = "";
$count           = 0;
$max             = 1000;
$day             = time() - (8 * 60 * 60);
while ($count < $max)
{
  $out_file_name = sprintf($leo_name_format, $count);
  $count++;
  if (file_exists($out_file_name))
  {
    $age = filemtime($out_file_name);
    if ($age == FALSE)
      continue;
   if ($age < $day)
     unlink($out_file_name);
  }
} // while
// Now find the first available file
$count = 0;
while ($count < $max)
{
  $out_file_name = sprintf($leo_name_format, $count);
  $count++;
  if (file_exists($out_file_name))
    continue;
   break;
} // while
if ($count >= $max)
{
  echo "Error uploading the file.";
  exit("");
}
$lines = file($leo_file_name);
if (!$lines)
{
  echo "Error uploading file.<br>\n";
  exit("");
}
// Open the output file.
$out_file = fopen($out_file_name, 'w');
if (!$out_file)
{
  echo "Error uploading file.<br>\n";
  exit("");
}
$found = 0;
foreach ($lines as $line_num => $line)
{
  if ($line == "<?xml-stylesheet ekr_test?>\n")
  {
    $line = '<?xml-stylesheet type="text/xsl" href="leo_to_html.xsl"?>';
  }
  fwrite($out_file, $line);
}
fclose($out_file);
echo ($out_file_name);
?>
