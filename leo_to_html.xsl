<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:output method="html" version="1.0" encoding="UTF-8" indent="yes"/>

<!-- The default setting. Not needed unless there is a strip-space element. -->
  <!-- <xsl:preserve-space elements='leo_file nodes t'/> -->

<xsl:template match ='leo_file'>
<html>
  <head>
    <style>
        pre { background:#FFE7C6; }
        div.outlinepane {
          height: 3.0in;
        }
        div.bodypane,div.body-text {
          height: 2.0in;
        }
        div.tnode {
            visibility: hidden;
            height: 0;
        }
        div.node {
            position: relative;
            left: 20px;
            background:Khaki;
        }
    </style>
    <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.11.2/jquery.min.js"></script>
    <script>
      $(document).ready(function(){
        $("h1").click(function(){
          $(this).parent().children("div.node").toggle();
          // The parent div's id is v.x.
          // Find the tnode div whose id is t.x.
          console.clear();
          parent_id=$(this).parent().attr("id");
          if (parent_id) {
            target=$(this).parent().attr("id").substring(2);
              console.log("clicked:"+$(this).text())
              // console.log("parent:"+$(this).parent())
              // console.log("target:"+target)
            $(".tnode").each(function(){
              console.log($(this).attr("id"))
              target2=$(this).attr("id").substring(2);
              if (target === target2) {
                console.log("found:"+target2)
                $("pre.body-text").text($(this).text());
              };
            }); // end .each.
          };
        });
      });
    </script>
  </head>
  <body>
    <xsl:apply-templates select='tnodes'/>
    <div class="outlinepane">
      <xsl:apply-templates select='vnodes'/>
    </div>
    <div class="bodypane">
      <h1>Body Pane</h1>
      <pre class="body-text">body</pre>
    </div>
  </body>
</html>
</xsl:template>

<xsl:template match = 'tnodes'>
<div class="tnodes">
  <xsl:for-each select = 't'>
    <div class="tnode">
      <xsl:attribute name="id"><xsl:value-of select='@tx'/></xsl:attribute>
      <xsl:value-of select='.'/>
    </div>
  </xsl:for-each>
</div>
</xsl:template>

<xsl:template match = 'vnodes'>
  <xsl:for-each select = 'v'>
    <xsl:apply-templates select ='.'/>
  </xsl:for-each>
</xsl:template>

<xsl:template match='v'>
  <div class="node">
    <xsl:attribute name="id"><xsl:value-of select='@t'/></xsl:attribute>
    <h1><xsl:value-of select='vh'/></h1>
    <xsl:if test ='./v' >
      <xsl:apply-templates select = 'v'/>
    </xsl:if>
  </div>
</xsl:template>

</xsl:stylesheet>
