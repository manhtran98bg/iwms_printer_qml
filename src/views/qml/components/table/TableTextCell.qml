import QtQuick 2.15

Item {
    id: root

    property string displayText: "---"
    property bool emptyRow: false
    property color textColor: "#ffffff"
    property color emptyTextColor: "#70839b"

    anchors.fill: parent

    Text {
        anchors.fill: parent
        anchors.leftMargin: 12
        anchors.rightMargin: 12
        text: root.emptyRow ? "---" : root.displayText
        color: root.emptyRow ? root.emptyTextColor : root.textColor
        font.pixelSize: 14
        verticalAlignment: Text.AlignVCenter
        horizontalAlignment: Text.AlignHCenter
        wrapMode: Text.WordWrap
        maximumLineCount: 3
        elide: Text.ElideRight
    }
}
