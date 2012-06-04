// import QtQuick 1.0 // to target S60 5th Edition or Maemo 5
import QtQuick 1.1

Rectangle {
    width: 360
    height: 360

    Component {
        id: nodeDelegate

        Item {
            height: childrenRect.height + 10
            width: flick.width

            Text {
                id: htext
                text: h
                font.pixelSize: 12
                anchors.left: btext.left
                anchors.top: parent.top
                anchors.topMargin: 4
                color: "gray"
            }

            TextEdit {

                id: btext
                text: b
                anchors.top: htext.bottom
                anchors.left: parent.left
                anchors.leftMargin: 4 + level * 20
                anchors.topMargin: 4

                Rectangle {
                    anchors.fill: parent
                    anchors {
                        leftMargin: -2
                        rightMargin: -2
                        topMargin: -2
                        bottomMargin: -2
                    }
                    border.color: parent.focus ? "blue" : "gray"
                    border.width: parent.focus ? 2 : 1
                    z: parent.z - 1
                }
            }
        }

    }

    Flickable {
        id: flick
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
