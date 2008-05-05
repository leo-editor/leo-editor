<?php /*Cascade Style Sheet style1.css*/
?>
<link href="../stex.css" rel="stylesheet" type="text/css" />

<?php
/*
Choice of language for website yes/no
*/
$ADD_LANGUAGE_CHOICE = 'yes';
/*
If 'Yes' you need to create images based on content/filename.htm
ex: /imgs/bttns_index.jpg
$NAV_IMAGES ='yes';
*/

?>

<?php /* Contact information */
$domain = "domain.com";

?>

<?php /* Content Script; reads .htm files in Content Directory */

//-- first section ends, second section begins

include('language.php');

$mycontentdir = "content"."/".$mylanguage;
if ($main_page == "") $main_page = "index";


$pagename = $main_page;
$ptitle = $company . " " . $main_page . " page " . $tel ." " . $city .
" " . $state . " " . $zip;

$main_page = "" . $main_page . ".htm";

/* if (is_file("$mycontentdir/$main_page")) {
$open = fopen("$mycontentdir/$main_page", "r");
$size = filesize("$mycontentdir/$main_page");
$content = fread($open, $size); */
//}
?>

<?php
/*Echo's Website*/
function hpo(){
echo '<div class="hpo">whatever text goes here</a> </div>';
}
?>
