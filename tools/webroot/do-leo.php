<?php
$DEBUG = 0;
/*************************************************************************/
/*
 * Support php script for load-leo.html
 *
 * Project purpose:
 *   Allow anyone to go to http://leo-editor.com/load-leo.html and use that
 *   html file to create a read-only version of the original leo file
 *   displayed in a meaningfull way by the web browser.
 *
 * Project operational summary:
 *   -An operator arrives at http://leo-editor.com/load-leo.html
 *   -The operator chooses a file either on their own hard drive, or on
 *    the Internet somewhere
 *   -With either choice, this php script receives, from the web page,
 *    either the name of the file to upload, or the name of a temporary
 *    file that has already been created in the php temp directory by the
 *    javascript in load-leo.html.
 *   -If this script receives the name of a temp file, then the contents
 *    of the target leo file already exist in the web server's file system
 *    in the form of a temporary file which will be deleted as soon as this
 *    script goes out of scope.
 *   -If this script receives the url of a file on the Internet, the script 
 *    knows to use that url as the source for the leo file to display.
 *   -This scripts reads the contents of the source leo file
 *   -This script then injects a reference to
 *    http://www.leoeditor.com/leo_to_html.xsl into the destination file
 *    if such a reference does not already exist in the destination file.
 *   -This script then writes the resulting file to a temporary file in the
 *    /tmp directory. The name format for the temporary file name is:
 *      show-leo-<16-hex-digit-random-name>.leo
 *   -This script then returns the file name to the calling load-leo.html
 *    file (Or an error message).
 *   -show-leo.html then either displays the error message, or changes
 *    document.location to the newly created leo file.
 *   -If show-leo.html changes its page location to the new temporary
 *    file, the apache server renders the page as xml to the browser, using
 *    the html-to_leo.xsl file as a stylesheet during the rendering.
 *
 * Notes:
 *   -This php script has only been tested using Firefox browsers.
 *   -The maximum file size for viewing is 10M.
 *   -leoeditor.com is hosted on a system using an Apache server, whose
 *    settings allow the placement of .htaccess in any root directory.
 *   -The .htaccess file in the root of leoeditor.com has been altered to
 *    request that apache consider all files ending in .leo to be treated
 *    as .xml files.
 *   -The line added to .htaccess is:
 *
 *       AddType application/xml leo
 *
 *   -Each time this script is run, the /tmp directory is scanned and any
 *    files older than 8 hours are removed. This serves as temporary file
 *    garbage collection.
 *   -In addition to scanning for older files, the entire contents of the
 *    /tmp directory are examined for total size. If the size exceeds
 *    500M, files are deleted, oldest first until the directory contents
 *    are less than 400M.
 *   -The maximum size for a single leo file is set by the php and apache
 *    setup. On this particular site, the max size is 64M. However, we
 *    limit the size to 10M.
 *   -Previous versions of this script placed a limit of 1000 users with
 *    concurrent access to this service. This restriction has been removed
 *    so there is no longer any artificial limit as to how many users may
 *    use this service at the same time.
 */
/*************************************************************************/
// Globals
/*************************************************************************/
$AMeg           = 1048576; // 1M
$Error_Message  = "\n" . '<br><p style="font-weight:900;">';
$Error_Message .= "Error uploading file</p><br>\n";
$File_Size      = 0;
$Is_Local       = false;
$Max_File_Size  = $AMeg * 10;
$Leo_Ext        = "leo";
if (!$DEBUG)
{
  // If not testing
  $Max_Storage_Size = $AMeg * 500;
  $Shrink_Size      = $Max_Storage_Size - ($AMeg * 100);
  $Temp_Dir         = getcwd() . "/tmp";
}
else
{
  // If testing
  $Max_Storage_Size = 339834;
  $Shrink_Size      = 21866;
  $Temp_Dir         = getcwd() . "/tmp1";
}
/*************************************************************************/
// Functions start here
/*************************************************************************/

// Return an error message, exit script
function error_exit()
{
  global $Error_Message;
  echo   $Error_Message;
  exit("");
} // error_exit

/*************************************************************************/

// Get the temp file name containing the data, or the remote url containing
// the data
function get_source_name()
{
  global $Is_Local;
  $Is_Local = false;
  foreach($_POST as $key => $value)
  {
    if ($key == "MAX_FILE_SIZE")
    {
      $name = $_FILES['Filedata']['tmp_name'];
      if ($name == "")
      {
        echo "<br>" . "File is too large or file name has an error." . "<br>";
        error_exit();
      }
      $Is_Local = true;
      return $name;
    }
  }
  $name     = $_POST['get_name'];
  if ($name == "")
  {
    echo "<br>" . "File is too large or file name has an error." . "<br>";
    error_exit();
  }
  return $name;
} // get_source_name

/*************************************************************************/

// Age out one file. It can't be a directory. If it is 8 hours old, kill
// it.
function age_file($filename)
{
  $day = time() - (8 * 60 * 60);
  if (file_exists($filename))
  {
    if (is_dir($filename))
      return true;
    $age = filemtime($filename);
      if ($age === false)
        return true;
    if ($age < $day)
      unlink($filename);
      return true;
  }
  return false;
} // age_file

/*************************************************************************/

// Delete files from the directory, oldest first, until the size is below
// the target size.

function size_directory()
{
  global $Max_Storage_Size;
  global $Shrink_Size;
  global $Temp_Dir;
  // sorting routine, sort by file age, oldest will be at the top of the
  // array
  function cmp($a, $b)
  {
    if ($a == $b)
      return 0;
    return ($a < $b) ? -1 : 1;
  }
  $filelist = array();
  $count    = 0;
  $handle = opendir($Temp_Dir);
  if (!$handle)
  {
    echo "<br>" . "File is too large or file name has an error." . "<br>";
    error_exit();
  }
  while (false !== ($entry = readdir($handle)))
  {
    if ($entry == ".")  continue;
    if ($entry == "..") continue;
    $fullname = $Temp_Dir . "/" . $entry;
    $filelist[$entry] = filemtime($fullname);
    $size += filesize($fullname);
    ++$count;
    if ($count > 500)
      break;
  } // while
  $keys = array_keys($filelist);
  if ($size < $Max_Storage_Size)
    return;
  uasort($filelist, cmp);
  $count = 0;
  $keys  = array_keys($filelist);
  foreach ($keys as $file_num => $fname)
  {
    $fullname = $Temp_Dir . "/" . $fname;
    $fsize = filesize($fullname);
    unlink($fullname);
    $size -= $fsize;
    if ($size < 0)
      $size = 0;
    if ($size < $Max_Storage_Size - $Shrink_Size)
      break;
    ++$count;
    if ($count > 10000)
      break;
  } // foreach
}
/*************************************************************************/

// 1. Age out any old temp files. We only age out 10000 at a time ;)
// 2. Check total size of directory and delete files, oldest first, if our
//    size limit has been exceeded.
function age_directory()
{
  global $Max_Storage_Size;
  global $Temp_Dir;
  $size  = 0;
  $count = 0;
  // Age old files
  $handle = opendir($Temp_Dir);
  if (!$handle)
  {
    echo "<br>" . "File is too large or file name has an error." . "<br>";
    error_exit();
  }
  while (false !== ($entry = readdir($handle)))
  {
    if ($entry == ".")  continue;
    if ($entry == "..") continue;
    $data = $Temp_Dir . "/" . $entry;
    if (!age_file($data))
      $size += filesize($data);
    ++$count;
    if ($count > 10000)
      break;
  }
  closedir($handle);
  if ($size >= $Max_Storage_Size)
    return size_directory();
} // age_directory

/*************************************************************************/

// Create a random hex string. Maximum length is 32.
function get_random_hex_string($length)
{
   $res = "";
   $count = 0;
   if ($length < 1)
     return "";
   if ($length > 32)
     $length = 32;
   while (strlen($res) < $length)
   {
     ++$count;
     if ($count > 33)
     {
       echo "<br>" . "File is too large or file name has an error." . "<br>";
       error_exit();
     }
     $temp = dechex(mt_rand());
     $res = $res . $temp;
     if (strlen($res) == $length)
       return $res;
     if (strlen($res) > $length)
       return substr($res, 0, $length);
   }
} // get_random_hex_string

/*************************************************************************/

// Create the output file object
function create_out_file()
{
   global $Temp_Dir;
   $stub = get_random_hex_string(16);
   if ($stub == "")
   {
     echo "<br>" . "Cannot create the temporary file on the web site." . "<br>";
     error_exit();
   }
   $name = "show-leo-" . $stub . ".leo";
   $file_object = fopen($Temp_Dir . "/" . $name, "w");
   if (!$file_object)
   {
     echo "<br>" . "Cannot create the temporary file on the web site." . "<br>";
     error_exit();
   }
   return array($name, $file_object);
} // create_out_file

/*************************************************************************/

// Check that this is a valid leo file name, and that the file size is
// ok.

function validate_file($name)
{
  global $File_Size;
  global $Is_Local;
  global $Leo_Ext;
  global $Max_File_Size;
  $File_Size = 0;
  if ($Is_Local)
  {
    // Can't check the name, because it has been named by javascript
    // using a temp file routine. Size should already be ok, but check
    // anyway to make sure we can stat the file.
    $File_Size = filesize($name);
    if (($File_Size > $Max_File_Size) || $File_Size == 0)
    {
      echo "<br>File is too large<br>\n";
      error_exit();
    }
    return;
  }
  // check name
  $extension = pathinfo($name, $options = PATHINFO_EXTENSION);
  if ($extension != $Leo_Ext)
  {
    echo "<br>The file must end in .leo<br>\n";
    error_exit();
  }
  // check size
  $headers = get_headers($name);
  foreach($headers as $h)
  {    // split is deprecated. See Leo issue #1551
    // $chunks = split(":", $h);    $chunks = explode(":", $h);
    $type   = $chunks[0];
    if ($type == "Content-Length")
      $File_Size = $chunks[1];
  }
  if ($File_Size > $Max_File_Size || $File_Size <= 0)
  {
    echo "<br>File is too large<br>\n";
    error_exit();
  }
  //echo "<br>File Size = ". $File_Size . "<br>\n";
}


/*************************************************************************/

// Read the source file into memory. If the file is too large to read all-
// at-once, php will barf, which is what we want. We will also enforce our
// own size limit
function read_source_file($name)
{
  validate_file($name);
  $lines = file($name);
  if (!$lines)
  {
    echo("<br>Can't read this file.<br>");
    error_exit();
  }
  return $lines;
} // read_source_file

/*************************************************************************/
// Script execution starts here
/*************************************************************************/

// Age out any existing old tmp files
age_directory();

// Either get the source script name
if (!$DEBUG)
{
  $script_name = get_source_name();
}

// Or use the following for testing
else
{
  $git_root    = "https://raw.githubusercontent.com/";
  $leo_root    = "leo-editor/leo-editor/master/";
  $script_name = $git_root . $leo_root . "leo/doc/CheatSheet.leo";
}

// Read the file contents into memory. Make sure it exists and is not too
// large.
$lines = read_source_file($script_name);

// Create the output file object
list($out_file_name, $out_file) = create_out_file();

/*************************************************************************/
// Read the first 10 lines of the file to see if there is an old reference
// to ekr_test or a new reference to leo_to_html.xsl. If there is a
// reference to leo_to_html.xsl, do nothing about such reference. If there
// is a reference to ekr_test, replace this reference with a reference to
// leo_to_html.xsl. If there is no reference to leo_to_html.xsl, inject
// a reference on line 2 of the file.
$false_line  = '<?xml-stylesheet type="text/xsl" href="http://leoeditor.';
$false_line .= 'com/leo_to_html.xsl"?>';

$inject_line_two = true;
$change_ekr_test = false;
foreach ($lines as $line_num => $line)
{
  if(strstr($line, "?xml-stylesheet ekr_test?"))
  {
    $change_ekr_test = true;
    $inject_line_two = false;
    if ($line_num == 10)
      break;
  }
} // foreach
foreach ($lines as $line_num => $line)
{
  if(strstr($line, "leo_to_html.xsl"))
  {
    if (!strstr($line, $false_line))
    {
      $change_ekr_test = false;
      $inject_line_two = false;
      if ($line_num == 10)
        break;
    }
  }
} // foreach

/*************************************************************************/
// Write the output file one line at a time. Insert the xsl reference if
// needed
$insert  = '<?xml-stylesheet type="text/xsl"';
$insert .= ' href="/leo_to_html.xsl"?>' . "\n";
foreach ($lines as $line_num => $line)
{
  if ($line_num == 2)
  {
    if ($inject_line_two)
      fwrite($out_file, $insert);
  }
  if ($line == "<?xml-stylesheet ekr_test?>\n")
  {
    if ($change_ekr_test)
      $line = $insert;
  }
  fwrite($out_file, $line);
} // foreach
fclose($out_file);
echo $out_file_name;
// The following lines for testing only
//echo "<br>out_file_name = " . $out_file_name . "<br>\n";
//echo "<br>Good Return<br>\n";
/*************************************************************************/
?>
