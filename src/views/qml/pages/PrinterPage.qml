import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Item {
    id: root

    required property var viewModel
    property string clockText: Qt.formatDateTime(new Date(), "yyyy-MM-dd hh:mm")
    property color pageColor: "#0d141d"
    property color panelColor: "#151e29"
    property color panelAltColor: "#101923"
    property color borderColor: "#2B3A52"
    property color textColor: "#ffffff"
    property color mutedTextColor: "#70839b"
    property color accentColor: "#2081ef"
    property color successColor: "#22c55e"
    property color dangerColor: "#ef4444"

    Rectangle {
        anchors.fill: parent
        color: root.pageColor
        z: -1
    }

    Timer {
        interval: 30000
        running: true
        repeat: true
        onTriggered: root.clockText = Qt.formatDateTime(new Date(), "yyyy-MM-dd hh:mm")
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        // Header section
        Rectangle {
            Layout.fillWidth: true
            height: 66
            color: root.panelColor
            border.color: root.borderColor

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 22
                anchors.rightMargin: 22
                spacing: 16

                Label {
                    Layout.fillWidth: true
                    text: root.viewModel.app_title
                    font.pixelSize: 24
                    font.bold: true
                    color: root.textColor
                    elide: Text.ElideRight
                }

                Rectangle {
                    implicitWidth: apiBadgeContent.implicitWidth + 22
                    implicitHeight: 30
                    radius: 15
                    color: root.viewModel.api_running ? "#052e1a" : "#3a1014"
                    border.color: root.viewModel.api_running ? "#166534" : "#991b1b"

                    Row {
                        id: apiBadgeContent
                        anchors.centerIn: parent
                        spacing: 8

                        Rectangle {
                            width: 8
                            height: 8
                            radius: 4
                            anchors.verticalCenter: parent.verticalCenter
                            color: root.viewModel.api_running ? root.successColor : root.dangerColor
                        }

                        Label {
                            text: root.viewModel.api_running ? "\u0110ang ch\u1ea1y API" : "API \u0111\u00e3 d\u1eebng"
                            color: root.viewModel.api_running ? "#86efac" : "#fca5a5"
                            font.pixelSize: 13
                            font.bold: true
                        }
                    }
                }
            }
        }

        Item {
            Layout.fillWidth: true
            implicitHeight: 12
        }

        // Page tab section
        Rectangle {
            Layout.fillWidth: true
            implicitHeight: 62
            Layout.leftMargin: 20
            Layout.rightMargin: 20

            color: root.panelColor
            border.color: root.borderColor

            TabBar {
                id: pageTabs
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.verticalCenter: parent.verticalCenter
                anchors.leftMargin: 20
                anchors.rightMargin: 20

                TabButton {
                    Layout.fillWidth: true
                    text: "In th\u1eed"
                    implicitHeight: 40
                    contentItem: Text {
                        text: parent.text
                        color: parent.checked ? "#ffffff" : root.mutedTextColor
                        font.pixelSize: 15
                        font.bold: parent.checked
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                    background: Rectangle {
                        color: parent.checked ? root.accentColor : root.panelColor
                        border.color: parent.checked ? root.accentColor : root.borderColor
                    }
                }

                TabButton {
                    Layout.fillWidth: true
                    implicitHeight: 40
                    text: "C\u00e0i \u0111\u1eb7t"
                    contentItem: Text {
                        text: parent.text
                        color: parent.checked ? "#ffffff" : root.mutedTextColor
                        font.pixelSize: 15
                        font.bold: parent.checked
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                    background: Rectangle {
                        color: parent.checked ? root.accentColor : root.panelColor
                        border.color: parent.checked ? root.accentColor : root.borderColor
                    }
                }
            }
        }

        StackLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.margins: 20
            currentIndex: pageTabs.currentIndex

            TestPrintTab {
                Layout.fillWidth: true
                Layout.fillHeight: true
                viewModel: root.viewModel
                panelColor: root.panelColor
                borderColor: root.borderColor
                textColor: root.textColor
            }

            SettingsTab {
                Layout.fillWidth: true
                Layout.fillHeight: true
                viewModel: root.viewModel
                panelColor: root.panelColor
                borderColor: root.borderColor
                textColor: root.textColor
                mutedTextColor: root.mutedTextColor
                accentColor: root.accentColor
            }

            
        }

        // Status bar section
        Rectangle {
            Layout.fillWidth: true
            height: 38
            color: root.panelColor
            border.color: root.borderColor

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 16
                anchors.rightMargin: 16
                spacing: 10

                Label {
                    Layout.fillWidth: true
                    text: root.viewModel.status
                    color: root.viewModel.api_running ? "#86efac" : root.textColor
                    elide: Text.ElideRight
                }

                Label {
                    text: root.clockText
                    color: root.mutedTextColor
                }
            }
        }
    }
}
