// import QtQuick 1.0 // to target S60 5th Edition or Maemo 5
import QtQuick 1.1

Rectangle {
    width: 360
    height: 360

    Component {
        id: nodeDelegate

        Item {
            height: childrenRect.height
            width: parent.parent.width

            Text {
                id: htext
                text: h
                font.pixelSize: 12
                anchors.right: btext.right
                color: "gray"
            }

            TextEdit {
                id: btext
                text: b
                anchors.top: htext.bottom
                anchors.left: parent.left


                Rectangle {
                    anchors.fill: parent
                    border.color: "blue"
                    border.width: 1
                    z: parent.z - 1
                }
            }
        }

    }

    Flickable {
        width: parent.width
        height: parent.height
        contentWidth:  parent.width
        contentHeight: col.height
        Column {
            id: col
            //anchors.fill: parent

            Repeater {
                model : nodesModel
                delegate: nodeDelegate


            }


        }

    }

}
