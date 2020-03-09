<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:output method="html" version="1.0" encoding="UTF-8" indent="yes"/>

<!-- The default setting. Not needed unless there is a strip-space element. -->
  <!-- <xsl:preserve-space elements='leo_file nodes t'/> -->

<xsl:template match ='leo_file'>
<html>
  <head>
    <!--
    <link rel="stylesheet" href="//cdnjs.cloudflare.com/ajax/libs/highlight.js/8.9.1/styles/default.min.css">
    <script src="//cdnjs.cloudflare.com/ajax/libs/highlight.js/8.9.1/highlight.min.js"></script>
    -->
    <style>
        /* pre { background:#FFE7C6; } */
        /* Must use h1 for nodes: see below. */
        h1 {
          font-size: 12pt;
          font-style: normal;
          font-weight: normal;
        }
        div.outlinepane {
          position: absolute;
          background: #ffffec; /* Leo yellow */
          top: 10px;
          height: 300px;
          width: 700px;
          overflow: scroll;
          line-height: 0.8;

        }
        div.bodypane {
          position: absolute;
          top: 310px;
          height: 300px;
          width: 700px;
          overflow: scroll;
        }
        div.tnode {
            visibility: hidden;
            height: 0;
        }
        div.node {
            position: relative;
            left: 20px;
        }
        div.node[has-children] > h1 {
            <!-- works -->
            <!-- background: red; -->
        }
    </style>

    <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.11.2/jquery.min.js"></script>
    <script>

      $(document).ready(function(){
        if (true) {
            // Toggle all but top-level nodes.
            // This requires an indication
            $(".node").toggle()
            $(".outlinepane").children(".node").toggle()
        } else {
            // Toggle all second-level nodes.
            // Safer, until we can see which nodes have children.
            $(".outlinepane").children(".node").children(".node").toggle()
        }
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
                // $("pre.body-text").text($(this).text());
                $("code").text($(this).text());
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
      <!-- <h4>Outline Pane</h4> -->
      <xsl:apply-templates select='vnodes'/>
    </div>
    <div class="bodypane">
      <!-- <h4>Body Pane</h4> -->
      <pre class="body-text"><code></code></pre>
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
    <xsl:choose>
      <xsl:when test ='./v' >
        <xsl:attribute name="has-children">1</xsl:attribute>
        <h1>+ <xsl:value-of select='vh'/></h1>
        <xsl:apply-templates select = 'v'/>
      </xsl:when>
      <xsl:when test ='vh' >
        <h1>- <xsl:value-of select='vh'/></h1>
      </xsl:when>
      <!--
      <xsl:otherwise>
        <h1>- <xsl:value-of select='vh'/></h1>
      </xsl:otherwise>
      -->
    </xsl:choose>
  </div>
</xsl:template>

</xsl:stylesheet>
