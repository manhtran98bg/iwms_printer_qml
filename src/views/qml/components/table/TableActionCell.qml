import QtQuick 2.15
import ".."

Item {
    id: root

    property string viewActionText: "View"
    property string executeActionText: "Execute"
    property bool executeEnabled: true

    signal viewRequested()
    signal executeRequested()

    anchors.fill: parent

    Row {
        anchors.centerIn: parent
        spacing: 8

        BaseButton {
            text: root.viewActionText
            variant: "outline"
            radius: 10
            font.pixelSize: 14
            implicitHeight: 40
            implicitWidth: 82
            onClicked: root.viewRequested()
        }

        BaseButton {
            text: root.executeActionText
            variant: "primary"
            radius: 10
            font.pixelSize: 14
            implicitHeight: 40
            implicitWidth: 92
            enabled: root.executeEnabled
            onClicked: root.executeRequested()
        }
    }
}
