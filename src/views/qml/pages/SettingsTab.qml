import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Dialogs
import QtQuick.Layouts 1.15
import "../components"

Item {
    id: root

    required property var viewModel
    property color panelColor: "#151e29"
    property color borderColor: "#2B3A52"
    property color textColor: "#ffffff"
    property color mutedTextColor: "#70839b"
    property color accentColor: "#2081ef"

    FileDialog {
        id: schemaDialog
        title: "Ch\u1ecdn file schema JSON"
        currentFolder: root.viewModel.schema_folder_url
        nameFilters: ["JSON files (*.json)", "All files (*)"]
        onAccepted: root.viewModel.set_data_path(String(selectedFile))
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 14

        // API server panel
        Rectangle {
            Layout.fillWidth: true
            implicitHeight: apiPanelLayout.implicitHeight + 32
            color: root.panelColor
            radius: 12
            border.color: root.borderColor

            ColumnLayout {
                id: apiPanelLayout
                anchors.fill: parent
                anchors.margins: 16
                spacing: 12

                Label {
                    text: "M\u00e1y ch\u1ee7 API"
                    color: root.textColor
                    font.pixelSize: 18
                    font.bold: true
                }

                GridLayout {
                    Layout.fillWidth: true
                    columns: 3
                    columnSpacing: 12
                    rowSpacing: 10

                    Label {
                        text: "\u0110\u01b0\u1eddng d\u1eabn"
                        color: root.textColor
                        font.pixelSize: 13
                    }

                    CustomTextBox {
                        Layout.fillWidth: true
                        text: root.viewModel.api_url
                        enabled: !root.viewModel.api_running
                        onEditingFinished: root.viewModel.set_api_url(text)
                    }

                    BaseButton {
                        Layout.preferredWidth: 128
                        text: root.viewModel.api_running ? "D\u1eebng" : "Kh\u1edfi \u0111\u1ed9ng"
                        variant: root.viewModel.api_running ? "danger" : "primary"
                        onClicked: root.viewModel.api_running
                            ? root.viewModel.stop_api()
                            : root.viewModel.start_api()
                    }
                }

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 24

                    Column {
                        Layout.preferredWidth: 190
                        spacing: 3

                        Label {
                            text: "Y\u00eau c\u1ea7u cu\u1ed1i"
                            color: root.mutedTextColor
                            font.pixelSize: 12
                        }

                        Label {
                            width: parent.width
                            text: root.viewModel.last_request_at
                            color: root.accentColor
                            font.pixelSize: 18
                            font.bold: true
                            elide: Text.ElideRight
                        }
                    }

                    Column {
                        Layout.preferredWidth: 130
                        spacing: 3

                        Label {
                            text: "Tr\u1ea1ng th\u00e1i"
                            color: root.mutedTextColor
                            font.pixelSize: 12
                        }

                        Label {
                            width: parent.width
                            text: root.viewModel.last_request_status
                            color: root.viewModel.last_request_status.indexOf("400") >= 0 ? "#fca5a5" : "#86efac"
                            font.pixelSize: 18
                            font.bold: true
                            elide: Text.ElideRight
                        }
                    }

                    Column {
                        Layout.preferredWidth: 130
                        spacing: 3

                        Label {
                            text: "S\u1ed1 request"
                            color: root.mutedTextColor
                            font.pixelSize: 12
                        }

                        Label {
                            width: parent.width
                            text: String(root.viewModel.request_count)
                            color: root.accentColor
                            font.pixelSize: 18
                            font.bold: true
                            elide: Text.ElideRight
                        }
                    }

                    Column {
                        Layout.preferredWidth: 120
                        spacing: 3

                        Label {
                            text: "Th\u1ea5t b\u1ea1i"
                            color: root.mutedTextColor
                            font.pixelSize: 12
                        }

                        Label {
                            width: parent.width
                            text: String(root.viewModel.failed_count)
                            color: root.viewModel.failed_count > 0 ? "#fca5a5" : "#86efac"
                            font.pixelSize: 18
                            font.bold: true
                            elide: Text.ElideRight
                        }
                    }

                    Item {
                        Layout.fillWidth: true
                    }
                }
            }
        }

        // Printer setup panel
        Rectangle {
            Layout.fillWidth: true
            implicitHeight: setupPanelLayout.implicitHeight + 32
            color: root.panelColor
            radius: 12
            border.color: root.borderColor

            ColumnLayout {
                id: setupPanelLayout
                anchors.fill: parent
                anchors.margins: 16
                spacing: 12

                Label {
                    text: "C\u00e0i \u0111\u1eb7t m\u00e1y in"
                    color: root.textColor
                    font.pixelSize: 18
                    font.bold: true
                }

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 12

                    Label {
                        Layout.preferredWidth: 110
                        text: "M\u00e1y in"
                        color: root.textColor
                        font.pixelSize: 13
                    }

                    CustomComboBox {
                        id: printerCombo
                        Layout.fillWidth: true
                        model: root.viewModel.printers

                        Component.onCompleted: {
                            var selectedIndex = root.viewModel.printers.indexOf(root.viewModel.printer_name)
                            if (selectedIndex >= 0) {
                                currentIndex = selectedIndex
                            }
                        }

                        Connections {
                            target: root.viewModel

                            function onPrintersChanged() {
                                var selectedIndex = root.viewModel.printers.indexOf(root.viewModel.printer_name)
                                printerCombo.currentIndex = selectedIndex >= 0 ? selectedIndex : -1
                            }

                            function onConfigChanged() {
                                var selectedIndex = root.viewModel.printers.indexOf(root.viewModel.printer_name)
                                if (selectedIndex >= 0) {
                                    printerCombo.currentIndex = selectedIndex
                                }
                            }
                        }

                        onActivated: root.viewModel.set_printer_name(currentText)
                    }

                    CustomButton {
                        Layout.preferredWidth: 96
                        text: "T\u1ea3i l\u1ea1i"
                        iconSource: "qrc:/icon_refresh"
                        onClicked: root.viewModel.refresh_printers()
                    }
                }

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 12

                    Label {
                        Layout.preferredWidth: 110
                        text: "C\u1ea5u tr\u00fac in"
                        color: root.textColor
                        font.pixelSize: 13
                    }

                    CustomTextBox {
                        Layout.fillWidth: true
                        text: root.viewModel.data_path
                        readOnly: true
                        placeholderText: "Ch\u01b0a ch\u1ecdn file"
                    }

                    CustomButton {
                        Layout.preferredWidth: 96
                        text: "Ch\u1ecdn"
                        iconSource: "qrc:/icon_browse"
                        onClicked: {
                            schemaDialog.currentFolder = root.viewModel.schema_folder_url
                            schemaDialog.open()
                        }
                    }
                }
            }
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.minimumHeight: 280
            color: root.panelColor
            radius: 12
            border.color: root.borderColor
            clip: true

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 16
                spacing: 12

                Label {
                    text: "Ảnh template tem"
                    color: root.textColor
                    font.pixelSize: 18
                    font.bold: true
                }

                Item {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    Layout.minimumHeight: 280

                    Image {
                        anchors.fill: parent
                        source: root.viewModel.template_preview_url
                        visible: root.viewModel.template_preview_available
                        fillMode: Image.PreserveAspectFit
                        asynchronous: true
                    }

                    Rectangle {
                        anchors.fill: parent
                        visible: !root.viewModel.template_preview_available
                        color: "#0f1722"
                        border.color: root.borderColor
                        radius: 6

                        Label {
                            anchors.centerIn: parent
                            text: "Không tồn tại"
                            color: root.mutedTextColor
                            font.pixelSize: 18
                            font.bold: true
                        }
                    }
                }
            }
        }
    }
}
