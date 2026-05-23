import QtQuick 2.15
import ".."

Item {
    id: root

    property string buttonText: "Remove"

    signal removeRequested()

    anchors.fill: parent

    BaseButton {
        anchors.centerIn: parent
        text: root.buttonText
        variant: "danger"
        radius: 10
        font.pixelSize: 13
        implicitHeight: 34
        implicitWidth: 86
        onClicked: root.removeRequested()
    }
}
