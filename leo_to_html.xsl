<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:template match='v'>
<ul type='square'>
    <xsl:variable name ='t' select ='@t' />
        <h1><xsl:value-of select='vh'/></h1>
        <xsl:for-each select='ancestor::leo_file/tnodes/t'>
            <xsl:if test="./attribute::tx=$t">
            <li>
                <pre>
                    <xsl:value-of select='.' />
                </pre>
            </li>
            </xsl:if>
        </xsl:for-each>

    <xsl:if test ='./v' >
        <xsl:apply-templates select = 'v'/>
    </xsl:if> 
 </ul>
</xsl:template>

<xsl:template match ='leo_file'>
<html>
    <head>
        <style>
            ul{ position:relative;right=25;
                border:thin ridge blue}
            li{ position:relative;right=25} 
            pre{ background:#FFE7C6 }       
        </style>
    </head>
    <body>
        <xsl:apply-templates select='vnodes'/>
    </body>
</html>
</xsl:template>

<xsl:template match = 'vnodes'>
    <xsl:for-each select = 'v'>
        <frame>
            <xsl:apply-templates select ='.'/>
        </frame>
    </xsl:for-each>
</xsl:template>

</xsl:stylesheet>
