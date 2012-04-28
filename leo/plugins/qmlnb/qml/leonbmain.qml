// import QtQuick 1.0 // to target S60 5th Edition or Maemo 5
import QtQuick 1.1

Rectangle {
    width: 360
    height: 360

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
                TextEdit {
                    text: b
                    Rectangle {
                        anchors.fill: parent
                        border.color: "blue"
                        border.width: 2
                        z: parent.z - 1
                    }
                }


            }


        }

    }

}
